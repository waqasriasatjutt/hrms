# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re
import json
import logging

import hashlib
import hmac

from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


class MercadoPagoWebhook(http.Controller):

    @http.route('/mercadopago/webhook', type='http', auth='none', methods=['POST'], csrf=False)
    def mercadopago_webhook(self, **kwargs):
        """Public webhook endpoint to receive MercadoPago notifications"""
        try:

            data = json.loads(request.httprequest.data.decode('utf-8'))
            if not data:
                _logger.warning('POST message received with no data')
                return http.Response(status=400)

            # Extract data from webhook payload
            webhook_data = data.get('data', {})
            application_id = data.get('application_id')
            external_reference = webhook_data.get('external_reference')
            payment_id = webhook_data.get('id')  # Este es el ID del recurso para la firma
            order_status = webhook_data.get('status')
            order_type = webhook_data.get('type')
            user_id = data.get('user_id')

            # Check for mandatory keys in header
            x_request_id = request.httprequest.headers.get('X-Request-Id')
            if not x_request_id:
                _logger.warning('POST message received with no X-Request-Id in header')
                return http.Response(status=400)

            x_signature = request.httprequest.headers.get('X-Signature')
            if not x_signature:
                _logger.warning('POST message received with no X-Signature in header')
                return http.Response(status=400)

            ts_m = re.search(r"ts=(\d+)", x_signature)
            v1_m = re.search(r"v1=([a-f0-9]+)", x_signature)
            ts = ts_m.group(1) if ts_m else None
            v1 = v1_m.group(1) if v1_m else None
            if not ts or not v1:
                return http.Response(status=400)

            # Find credential based on application_id (más preciso que user_id)
            credential_id = None
            credential = None

            if application_id:
                # Buscar por application_id primero
                credential = request.env['mp.credential'].sudo().search([('client_id', '=', str(application_id))],
                                                                        limit=1)
                if not credential and user_id:
                    # Fallback: buscar por user_id si no encontró por application_id
                    credential = request.env['mp.credential'].sudo().search([('user_id', '=', str(user_id))], limit=1)
            elif user_id:
                credential = request.env['mp.credential'].sudo().search([('user_id', '=', str(user_id))], limit=1)

            if credential:
                credential_id = credential.id

            if not credential:
                _logger.error('No credential found for application_id: %s or user_id: %s', application_id, user_id)
                return http.Response(status=401)

            # CLAVE ESTÁTICA TEMPORAL PARA DEBUGGING
            # TODO: Cambiar por credential.webhook_secret cuando esté configurado
            secret_key = credential.mp_webhook_secret

            _logger.info('Using STATIC secret_key for debugging: %s...', secret_key[:10])

            # Según documentación oficial de MercadoPago:
            # El data.id debe estar en MINÚSCULAS en el template
            payment_id_lower = payment_id.lower()

            # Template oficial: id:[data.id_url];request-id:[x-request-id_header];ts:[ts_header];
            # donde data.id_url debe estar en minúsculas
            official_template = f"id:{payment_id_lower};request-id:{x_request_id};ts:{ts};"

            _logger.info('Using official template with lowercase ID: %s', official_template)
            cyphed_signature = hmac.new(secret_key.encode(), official_template.encode(), hashlib.sha256).hexdigest()

            if not hmac.compare_digest(cyphed_signature, v1):

                # Intentar otros métodos de validación
                _logger.info('Trying alternative validation methods...')

                # Método 1: Sin el punto y coma final
                alt_template_1 = f"id:{payment_id_lower};request-id:{x_request_id};ts:{ts}"
                alt_signature_1 = hmac.new(secret_key.encode(), alt_template_1.encode(), hashlib.sha256).hexdigest()

                # Método 2: Con ID en mayúsculas
                alt_template_2 = f"id:{payment_id};request-id:{x_request_id};ts:{ts};"
                alt_signature_2 = hmac.new(secret_key.encode(), alt_template_2.encode(), hashlib.sha256).hexdigest()

                # Método 3: Solo valores sin prefijos
                alt_template_3 = f"{payment_id_lower};{x_request_id};{ts}"
                alt_signature_3 = hmac.new(secret_key.encode(), alt_template_3.encode(), hashlib.sha256).hexdigest()

                # Verificar si alguno coincide
                if (hmac.compare_digest(alt_signature_1, v1) or
                        hmac.compare_digest(alt_signature_2, v1) or
                        hmac.compare_digest(alt_signature_3, v1)):
                    _logger.info('Alternative method worked!')
                else:
                    _logger.error('All validation methods failed with static key')
                    return http.Response(status=401)

            else:
                _logger.info('Webhook signature verified successfully with static key!')

            # Create notification record
            notification_vals = {
                'name': external_reference,
                'payment_id': payment_id,
                'credential_id': credential_id,
                'type': order_type if order_type in ['point', 'qr'] else 'point',
                'status': order_status if order_status in ['processed', 'refunded', 'canceled', 'expired',
                                                           'action_required', 'failed'] else False,
                'request': json.dumps(data),
            }
            # Create the notification record
            mp_notification = request.env['mp.notifications'].sudo().create(notification_vals)
            # _logger.info("MercadoPago notification created: %s", mp_notification.id)
            return Response("Operación completada con éxito.", status=200)

        except Exception as e:
            return Response(str(e), status=400)