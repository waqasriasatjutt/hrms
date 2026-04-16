# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import models, fields, api, _
import requests
import uuid
_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"

    mpqr_payment_token = fields.Char(string='Payment token')

    def mpqr_updating_order(self, order):
        pos_order_id = self.env['pos.order'].search([('access_token', '=', order['access_token_order'])])
        pos_order_id.write({'mpqr_payment_token': order['mpqr_payment_id']})
        return True

    def mpqr_make_cancel(self, order):
        """
        Cancela una orden de pago QR generada previamente mediante la API de Mercado Pago.

        Esta función envía una solicitud DELETE a la API de Mercado Pago para cancelar
        una orden de pago QR asociada a un pedido específico en POS.

        Parámetros:
            self (object): Instancia del modelo desde donde se llama la función.
            order (dict): Diccionario que contiene los datos del pedido, incluyendo:
                - 'pos_session_id': ID de la sesión POS actual.
                - 'payment_method_id': ID del método de pago utilizado.

        Retorna:
            dict: Diccionario con los siguientes campos:
                - 'status_code': Código HTTP de la respuesta (204 si fue exitoso).
                - 'success': Booleano indicando si la cancelación fue exitosa.
                - 'error': Mensaje de error en caso de fallo (solo presente si success == False).
        """

        try:
            # Obtener token
            transaction_id = order.get('access_token_payment')
            if not transaction_id:
                vals = {'status_code': 200, 'success': True}
                return vals
            notify_id = self.env['mp.notifications'].sudo().search(
                [('payment_id', '=', transaction_id)])
            if notify_id:
                if notify_id.status == 'expired':
                    vals = {
                        'status_code': 200,
                        'success': True,
                        'payment_status': 'expired',
                        'payment_id': transaction_id,
                    }
                    return vals
                if notify_id.status == 'failed':
                    vals = {
                        'status_code': 200,
                        'success': True,
                        'payment_status': 'failed',
                        'payment_id': transaction_id,
                    }
                    return vals
                if notify_id.status == 'processed':
                    vals = {
                        'status_code': 400,
                        'success': False,
                        'error': 'No se puede cancelar un pago ya procesado',
                        'payment_id': transaction_id,
                    }
                    return vals
                if notify_id.status == 'refunded':
                    vals = {
                        'status_code': 400,
                        'success': False,
                        'error': 'No puedes ser cancelado un pago devuelto.',
                        'payment_id': transaction_id,
                    }
                    return vals
            # Obtener sesión POS
            pos_session_id = self.env['pos.session'].sudo().browse(order.get('pos_session_id'))
            if not pos_session_id.exists():
                raise ValueError("La sesión POS no existe.")

            sale_point_id = pos_session_id.config_id.sale_point_id
            if not sale_point_id:
                raise ValueError("No se encontró un punto de venta asociado a la configuración de la sesión.")

            # Obtener método de pago
            payment_method_id = order.get('payment_method_id')
            pos_payment_method_id = self.env['pos.payment.method'].sudo().browse(payment_method_id)
            if not pos_payment_method_id.exists():
                raise ValueError(f"Método de pago con ID {payment_method_id} no encontrado.")

            configuration_id = pos_payment_method_id.pos_mp_config_id
            if not configuration_id:
                raise ValueError("Configuración MP QR no encontrada para este método de pago.")

            # Datos de autenticación
            user = configuration_id.user_id or ''
            access_token = configuration_id.mp_access_token or ''
            base_url = configuration_id.mp_url.strip('/')

            if not all([user, access_token, base_url]):
                raise ValueError("Faltan datos necesarios (usuario, token, idempotency_key o URL) en la configuración de Mercado Pago.")

            # Construir endpoint
            endpoint = f"{base_url}/v1/orders/{order['access_token_payment']}/cancel"
            idempotency_key = str(uuid.uuid4())
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
                'X-Idempotency-Key': idempotency_key,
            }
            response = requests.post(endpoint, headers=headers, timeout=10)
            if response.status_code == 200:
                vals = {'status_code': 200, 'success': True}
            else:
                response_data = response.json()
                if 'errors' in response_data and len(response_data['errors']) > 0:
                    first_error = response_data['errors'][0]
                    error_code = first_error.get('code')
                    error_message = first_error.get('message', 'Unknown error')

                    if error_code == 'cannot_cancel_order':
                        vals = {
                            'status_code': response.status_code,
                            'success': False,
                            'error': error_message  # ← Use the actual error message from the API
                        }
                    else:
                        # Handle other error codes
                        vals = {
                            'status_code': response.status_code,
                            'success': False,
                            'error': f"[{error_code}] {error_message}"
                        }
                else:
                    error_msg = response.json().get('message', 'Error desconocido')
                    vals = {'status_code': response.status_code, 'success': False, 'error': error_msg}
            # Registrar log
            self.env['mp.log'].sudo().create_logs(
                pos_session_id,
                'remove_order',
                headers,
                idempotency_key,
                endpoint,
                response.status_code,
                '',
                ''
            )

        except Exception as e:
            _logger.exception("Excepción al procesar la cancelación de pago por MPQR")
            vals = {'status_code': 500, 'success': False, 'error': str(e)}

        return vals

    def mpqr_get_payment_status(self, order):
        """
        Obtiene el estado actual de un pago QR realizado mediante la API de Mercado Pago.

        Esta función consulta el estado del pago usando el 'external_reference' del pedido,
        el cual corresponde al UID del mismo. Retorna información clave como el estado
        del pago y su ID si fue encontrado.

        Parámetros:
            self (object): Instancia del modelo desde donde se llama la función.
            order (dict): Diccionario que contiene los siguientes campos:
                - 'pos_session_id': ID de la sesión POS actual.
                - 'payment_method_id': ID del método de pago usado.
                - 'order_uid': UID externo del pedido para buscar el pago.

        Retorna:
            dict: Diccionario con los siguientes campos:
                - 'status_code': Código HTTP de la respuesta (200 si fue exitoso).
                - 'payment_status': Estado del pago (ej: 'approved', 'pending', etc.).
                - 'payment_id': ID del pago en Mercado Pago (si se encontró).
                - 'error': Mensaje de error en caso de fallo (solo presente si status_code != 200).
        """
        try:
            # Obtener sesión POS
            transaction_id = order.get('access_token_payment')
            order_external_reference = order.get('order_uid')
            is_order_refund = order['isRefundOrder']

            # Obtener sesión POS
            pos_session_id = self.env['pos.session'].sudo().browse(order.get('pos_session_id'))
            notify_id = self.env['mp.notifications'].sudo().search(
                [('payment_id', '=', transaction_id), ('name', '=', order_external_reference)])

            if notify_id.status in ['processed', 'refunded'] or is_order_refund:
                vals = {
                    'status_code': 200,
                    'payment_status': 'processed',
                    'payment_id': transaction_id,
                }
                return vals
            if notify_id.status == 'expired':
                vals = {
                    'status_code': 400,
                    'payment_status': 'expired',
                    'error': 'El pago expiró, por favor cancele el pago y vuelva a intentar.',
                    'payment_id': transaction_id,
                }
                return vals

            if notify_id.status == 'failed':
                vals = {
                    'status_code': 400,
                    'payment_status': 'failed',
                    'error': 'El pago falló, por favor cancele el pago y vuelva a intentar.',
                    'payment_id': transaction_id,
                }
                return vals

            if not pos_session_id.exists():
                raise ValueError("La sesión POS no existe.")

            # Obtener método de pago
            payment_method_id = order.get('payment_method_id')
            pos_payment_method_id = self.env['pos.payment.method'].sudo().browse(payment_method_id)
            if not pos_payment_method_id.exists():
                raise ValueError(f"Método de pago con ID {payment_method_id} no encontrado.")

            configuration_id = pos_payment_method_id.pos_mp_config_id
            if not configuration_id:
                raise ValueError("Configuración MP QR no encontrada para este método de pago.")

            access_token = configuration_id.mp_access_token or ''
            base_url = configuration_id.mp_url.strip('/')

            if not all([access_token, base_url, transaction_id]):
                raise ValueError("Faltan parámetros necesarios: token, URL o UID del pedido.")

            # Construir endpoint
            endpoint = f"{base_url}/v1/orders/{transaction_id}"

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }

            response = requests.get(endpoint, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data and data['status'] != 'created':
                    vals = {
                        'status_code': 200,
                        'payment_status': data.get('status', 'unknown'),
                        'payment_id': data.get('id'),
                    }
                else:
                    vals = {
                        'status_code': 400,
                        'payment_status': 'not_found',
                        'error': 'Debe ser procesado el pago antes de ser validado.'
                    }
            else:
                error_msg = response.json().get('message', 'Error desconocido')
                _logger.error('Error al obtener estado del pago. Código: %d, Mensaje: %s', response.status_code,
                              error_msg)
                vals = {
                    'status_code': response.status_code,
                    'error': error_msg
                }

            # Registrar log
            self.env['mp.log'].sudo().create_logs(
                pos_session_id,
                'get_order',
                headers,
                '',
                endpoint,
                response.status_code,
                '',
                response.json() if response.content else ''
            )

        except Exception as e:
            _logger.exception("Excepción al obtener el estado del pago por MPQR")
            vals = {'status_code': 500, 'error': str(e)}

        return vals

    def mpqr_make_refunds(self, order):
        """
        Realiza un reembolso (refund) de un pago QR ya realizado a través de Mercado Pago.

        Esta función llama a la API de Mercado Pago para generar un reembolso parcial o total
        sobre un pago identificado por su token. Se utiliza el campo 'mpqr_payment_token'
        del pedido POS y se genera una clave de idempotencia única.

        Parámetros:
            self (object): Instancia del modelo desde donde se llama la función.
            order (dict): Diccionario con los siguientes campos:
                - 'toRefundLines_ids': Lista de IDs de órdenes POS a reembolsar.
                - 'payment_method_id': ID del método de pago usado.
                - 'amount_total': Monto total a reembolsar.

        Retorna:
            dict: Diccionario con los siguientes campos:
                - 'status_code': Código HTTP de la respuesta (201 si fue exitoso).
                - 'refund_id': ID del reembolso generado por Mercado Pago (si aplica).
                - 'error': Mensaje de error en caso de fallo (solo presente si status_code != 201).
        """
        try:
            # Obtener orden POS a reembolsar
            pos_order_id = self.env['pos.order'].browse(order['original_pos_order_id'])
            if not pos_order_id:
                raise ValueError("No se proporcionaron órdenes para reembolsar.")

            # Obtener método de pago
            payment_method_id = order.get('payment_method_id')
            pos_payment_method_id = self.env['pos.payment.method'].sudo().browse(payment_method_id)
            if not pos_payment_method_id.exists():
                raise ValueError(f"Método de pago con ID {payment_method_id} no encontrado.")

            configuration_id = pos_payment_method_id.pos_mp_config_id
            if not configuration_id:
                raise ValueError("Configuración MP QR no encontrada para este método de pago.")

            access_token = configuration_id.mp_access_token or ''
            base_url = configuration_id.mp_url.strip('/')
            idempotency_key = str(uuid.uuid4())

            if not all([access_token, base_url]):
                raise ValueError("Faltan datos necesarios (token, idempotency_key o URL) en la configuración de Mercado Pago.")

            transaction_id = pos_order_id.mpqr_payment_token
            if not transaction_id:
                raise ValueError("El pago no tiene un token válido para realizar el reembolso.")

            # Construir endpoint
            endpoint = f"{base_url}/v1/orders/{transaction_id}/refund"

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
                'X-Idempotency-Key': idempotency_key
            }
            response = requests.post(endpoint, headers=headers, timeout=10)
            if response.status_code == 201:
                refund_data = response.json()
                refund_id = refund_data.get('id')
                vals = {
                    'status_code': 200,
                    'state': refund_data['status'],
                    'transaction_id': refund_id
                }
            else:
                error_msg = response.json().get('message', 'Error desconocido')
                _logger.error('Error al procesar el reembolso. Código: %d, Mensaje: %s', response.status_code,
                              error_msg)
                vals = {
                    'status_code': response.status_code,
                    'error': error_msg,
                    'state': 'Unauthorized',
                }

            # Registrar log
            self.env['mp.log'].sudo().create_logs(
                pos_order_id.session_id,
                'refund_order',
                headers,
                idempotency_key,
                endpoint,
                response.status_code,
                '',
                response.json() if response.content else ''
            )

        except Exception as e:
            _logger.exception("Excepción al procesar el reembolso por MPQR")
            vals = {'status_code': 500, 'error': str(e)}
        return vals









