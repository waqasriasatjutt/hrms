# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import requests
import json
import logging
import uuid
from odoo import models, fields, api, _
_logger = logging.getLogger(__name__)


class PoSPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    pos_mp_config_id = fields.Many2one('mp.credential', string='MP Credentials', help='The configuration of MP used for this journal')

    def _get_payment_terminal_selection(self):
        return super(PoSPaymentMethod, self)._get_payment_terminal_selection() + [('mpqr', 'MP QR')]

    @api.onchange('use_payment_terminal')
    def _onchange_use_payment_terminal(self):
        super(PoSPaymentMethod, self)._onchange_use_payment_terminal()
        if self.use_payment_terminal != 'mpqr':
            self.pos_mp_config_id = False

    def mpqr_make_payment(self, pos_session, amount, order_uid, order_lines=None):
        """
            Realiza un pago mediante el sistema de QR de Mercado Pago para un pedido en POS.

            Esta función genera una orden de pago vía API de Mercado Pago In-Store QR,
            utilizando los datos de configuración del método de pago seleccionado y la sesión POS activa.

            Parámetros:
                self (object): Instancia del modelo desde donde se llama la función.
                pos_session (int): ID de la sesión POS actual.
                amount (float): Monto total a cobrar.
                order_uid (str): Identificador único del pedido (external_reference en MP).

            Retorna:
                dict: Diccionario con los siguientes campos:
                    - 'status_code': Código HTTP de la respuesta (200 si fue exitoso).
                    - 'payment_id': ID del pago (en este caso es igual a order_uid si fue exitoso).
                    - 'error': Mensaje de error en caso de fallo (solo presente si status_code != 200).
            """
        try:
            # Obtener sesión POS
            pos_session_id = self.env['pos.session'].sudo().browse(pos_session)
            if not pos_session_id.exists():
                raise ValueError("La sesión POS no existe.")

            sale_point_id = pos_session_id.config_id.sale_point_id
            if not sale_point_id:
                raise ValueError("No se encontró un punto de venta asociado a la configuración de la sesión.")

            # Obtener método de pago
            pos_payment_method_id = self.env['pos.payment.method'].sudo().browse(self.id)
            if not pos_payment_method_id.exists():
                raise ValueError("Método de pago no encontrado.")

            configuration_id = pos_payment_method_id.pos_mp_config_id
            if not configuration_id:
                raise ValueError("Configuración MP QR no encontrada para este método de pago.")

            # Datos de autenticación
            user_id = configuration_id.user_id or ''
            access_token = configuration_id.mp_access_token or ''
            platform_id = configuration_id.platform_id
            integrator_id = configuration_id.integrator_id
            url = configuration_id.mp_url.strip('/')  # Limpiar URL base
            
            # Obtener external_store_id y external_pos_id del sale_point_id
            external_store_id = sale_point_id.external_store_id or ''
            external_pos_id = sale_point_id.external_id or ''

            if not all([user_id, access_token, url, external_store_id, external_pos_id]):
                raise ValueError("Faltan datos necesarios (user_id, token, external_store_id, external_pos_id o URL) en la configuración de Mercado Pago.")

            # Construir endpoint con el nuevo formato
            endpoint = f"{url}/v1/orders"
            idempotency_key = str(uuid.uuid4())

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
                'X-Idempotency-Key': idempotency_key,
                'x-platform-id': platform_id,
            }


            # Construir payload con el nuevo formato
            items = []
            if order_lines:
                for line in order_lines:
                    product_id = line.get('product_id')
                    qty = line.get('qty', 1)
                    price = line.get('price_unit', 0)
                    
                    # Obtener información del producto
                    product = self.env['product.product'].sudo().browse(product_id) if product_id else None
                    
                    items.append({
                        "title": product.name if product else "Producto",
                        "unit_price": str(float(price)),
                        "quantity": int(qty),
                        "unit_measure": "unit",
                        "external_code": product.default_code or f"PROD{product_id}" if product else "PRODUCT001",
                    })

            payload = {
                "type": "qr",
                "total_amount": str(float(amount)),
                "description": "Compra en punto de venta",
                "integration_data": {
                    "platform_id": platform_id,
                    "integrator_id": integrator_id,
                },
                "external_reference": order_uid,
                "items": items,
                "config": {"qr": {"external_pos_id": external_pos_id, "mode": "static"}},
                "transactions": {"payments": [{"amount": str(float(amount))}]},
            }

            response = requests.post(endpoint, headers=headers, data=json.dumps(payload), timeout=10)

            if response.status_code in [201, 204]:
                response_vals = response.json()
                vals = {'state': response_vals['status'], 'transaction_id': response_vals['id']}
            else:
                try:
                    error_data = response.json()
                    errors_list = error_data.get('errors', [])
                    if isinstance(errors_list, list) and len(errors_list) > 0:
                        first_error = errors_list[0]
                        error_msg = first_error.get('message', 'Error desconocido en estructura "errors"')
                        # ✅ Extraer 'details' si existe y es una lista
                        details = first_error.get('details')
                        if isinstance(details, list) and len(details) > 0:
                            # Unir todos los detalles en un solo string, separados por punto y coma o salto
                            details_str = "; ".join(str(d) for d in details)
                            error_msg += f" Detalles: {details_str}"
                    else:
                        error_msg = error_data.get('message') or error_data.get('error') or 'Error desconocido'
                except Exception:
                    error_msg = f'Error HTTP {response.status_code}'
                _logger.error('Error en respuesta de MPQR. Código: %d, Mensaje: %s', response.status_code, error_msg)
                vals = {'state': 'PAYMENT_FAILED', 'error': error_msg}

            # Registrar log
            self.env['mp.log'].sudo().create_logs(
                pos_session_id,
                'create_order',
                headers,
                idempotency_key,
                endpoint,
                response.status_code,
                payload,
                response.json()
            )

        except Exception as e:
            _logger.exception("Excepción al procesar pago por MPQR")
            vals = {'state': 'PAYMENT_FAILED', 'error': str(e)}

        return vals

