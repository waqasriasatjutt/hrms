# -*- coding: utf-8 -*-
# Copyright (C) 2024 Axcelere.
# Licensed under the GPL-3.0 License or later.

import logging
from odoo import api, fields, models, _
import json
import requests
from odoo.exceptions import UserError
from odoo.addons.pos_payway.models.payway_library import PROD_BASE_API_URL, TEST_BASE_API_URL, BASE_PATH_PAYMENT, BASE_PATH_REVERSAL, BASE_PATH_REFUNDS

_logger = logging.getLogger(__name__)


class PosPaymentMethod(models.Model):
    _inherit = "pos.payment.method"

    pos_payway_config_id = fields.Many2one('pos_payway.configuration', string='Credenciales Payway')
    payway_test_mode = fields.Boolean(string="Modo de prueba")
    card_brand = fields.Selection([('AMEX', 'AMEX')], string='Marca de tarjeta')
    payway_terminal_number = fields.Char(string="Identificador de terminal")
    terminal_operation = fields.Selection([('CARD', 'Tarjeta'), ('QR_CODE', 'QR')], string='Operación de la terminal')

    def _get_payment_terminal_selection(self):
        return super(PosPaymentMethod, self)._get_payment_terminal_selection() + [('payway', 'Payway')]

    @api.onchange('use_payment_terminal')
    def _onchange_use_payment_terminal(self):
        super(PosPaymentMethod, self)._onchange_use_payment_terminal()
        if self.use_payment_terminal != 'payway':
            self.pos_payway_config_id = False

    def payway_make_payment(self, pos_session, installment, amount):
        _logger.info('************************* Enviando solicitud de pago a Payway ******************************')

        # Buscar sesión y datos necesarios
        pos_session_id = self.env['pos.session'].browse(pos_session)
        if not pos_session_id.exists():
            _logger.error("La sesión POS con ID %s no existe.", pos_session)
            raise UserError("Sesión POS no encontrada.")

        config = pos_session_id.config_id
        pos_payment_method = self.env['pos.payment.method'].browse(self.id)

        if not pos_payment_method.exists():
            _logger.error("Método de pago no encontrado (ID: %s).", self.id)
            raise UserError("Método de pago no encontrado.")

        # Verificar y actualizar token si es necesario
        config._ensure_valid_token()

        # Determinar URL base según modo de prueba
        base_url = TEST_BASE_API_URL if pos_payment_method.payway_test_mode else PROD_BASE_API_URL
        access_token = config.access_token or ''
        cuit_cuil = pos_payment_method.company_id.vat or ''

        if not access_token:
            _logger.error("No se encontró un token de acceso válido.")
            raise UserError("Token de acceso no disponible.")

        if not cuit_cuil:
            _logger.error("CUIT/CUIL no configurado para la empresa.")
            raise UserError("CUIT/CUIL no disponible.")

        # Construir endpoint
        endpoint = f"{base_url}{BASE_PATH_PAYMENT}/payments?cuit_cuil={cuit_cuil}"

        # Calcular cuota e interés
        surcharge_coefficient = 0.0
        installment_id = self.env['account.card.installment'].browse(installment)
        if installment_id.exists():
            surcharge_coefficient = installment_id.surcharge_coefficient
            installments_number = int(installment_id.installment)
        else:
            installments_number = 1

        # Formatear monto con recargo
        try:
            amount_total = float(amount)
            amount_with_surcharge = round(amount_total * surcharge_coefficient, 2)
            amount_total_str = f"{amount_with_surcharge:.2f}".replace('.', '')
        except Exception as e:
            _logger.error("Error al formatear el monto del pago: %s", str(e))
            raise UserError("Error al procesar el monto del pago.")

        # Datos del payload
        acquirer_id = pos_payment_method.pos_payway_config_id.payway_acquier_id or ''
        terminal_number = pos_payment_method.payway_terminal_number or ''

        if not terminal_number:
            _logger.error("Número de terminal Payway no configurado.")
            raise UserError("Terminal Payway no configurado.")

        payload = {
            "payment_request_data": {
                "subnet_acquirer_id": acquirer_id,
                "payment_amount": amount_total_str,
                "terminal_menu_text": f"Ref: ${amount_with_surcharge:.2f}",
                "ecr_provider": pos_payment_method.company_id.name,
                "ecr_name": pos_payment_method.company_id.name,
                "ecr_version": "1.0",
                "change_amount": "0",
                "ecr_transaction_id": None,
                "installments_number": installments_number,
                "bank_account_type": None,
                "payment_plan_id": None,
                "print_method": "MOBITEF_NON_FISCAL",
                "print_copies": "BOTH",
                "terminals_list": [{"terminal_id": terminal_number}],
                "card_brand_product": None,
                "terminal_operation_method": pos_payment_method.terminal_operation,
                "qr_benefit_code": True if pos_payment_method.terminal_operation == 'QR_CODE' else None,
                "trx_receipt_notes": None,
                "card_holder_id": None
            }
        }

        # Headers
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }

        # Log de la solicitud
        _logger.info('******************** Payload enviado a Payway *************************************************')
        _logger.info(json.dumps(payload, indent=2))

        # Hacer la solicitud
        try:
            response = requests.post(endpoint, headers=headers, data=json.dumps(payload), timeout=15)
        except requests.exceptions.RequestException as e:
            _logger.error("Error al conectar con Payway: %s", str(e))
            raise UserError("Error al conectar con Payway.")

        # Procesar respuesta
        _logger.info('********************** Respuesta del pago en Payway: %s %s **************************',
                     response.status_code, response.text)

        # Registrar log
        log_id = self.env['payway.log'].sudo().create_logs(
            pos_session_id,
            'create_order',
            headers,
            endpoint,
            response.status_code,
            payload,
            response.json()
        )

        if response.status_code == 200:
            try:
                data = response.json()
                payment_data = data.get('payment_data', {})
                log_id.write({'payment_id': payment_data.get('payment_id')})
                vals = {
                    'status_code': 200,
                    'transaction_id': payment_data.get('payment_id'),
                    'state': payment_data.get('payment_status'),
                }
            except ValueError:
                _logger.error("Error al parsear la respuesta JSON.")
                vals = {
                    'status_code': response.status_code,
                    'error': 'Respuesta inválida del servidor.'
                }
        else:
            try:
                error_data = response.json()
                error_title = error_data.get('errors', [{}])[0].get('title', 'Error desconocido')
            except ValueError:
                error_title = 'Error desconocido'

            vals = {
                'status_code': response.status_code,
                'error': error_title
            }
        return vals


class PosOrder(models.Model):
    _inherit = "pos.order"

    payway_payment_token = fields.Char(string='Payment token')

    def payway_make_cancel(self, order):
        # Buscar sesión POS
        pos_session = self.env['pos.session'].browse(order.get('pos_session_id'))
        if not pos_session:
            return {'status_code': 404, 'error': 'POS session not found'}

        # Validar y actualizar token si es necesario
        pos_session.config_id._ensure_valid_token()

        # Obtener método de pago
        payment_method = self.env['pos.payment.method'].browse(order.get('payment_method_id'))
        if not payment_method:
            return {'status_code': 404, 'error': 'Payment method not found'}

        # Determinar ambiente (test o producción)
        base_url = TEST_BASE_API_URL if payment_method.payway_test_mode else PROD_BASE_API_URL

        # Datos de la solicitud
        access_token = pos_session.config_id.access_token or ''
        cuit_cuil = payment_method.company_id.vat
        subnet_acquirer_id = payment_method.pos_payway_config_id.payway_acquier_id
        transaction_id = order.get("access_token_payment")

        if not transaction_id:
            return {'status_code': 400, 'error': 'Missing transaction ID'}

        # Mapeo de tipos de pago
        payment_type = order.get('payment_type_build')
        if payment_type == 'reversals_refunds':
            if payment_method.card_brand == 'AMEX':
                recurse = BASE_PATH_REFUNDS
                payment_type = 'refunds'
            else:
                recurse = BASE_PATH_REVERSAL
                payment_type = 'reversals'
        else:
            recurse = BASE_PATH_PAYMENT
            payment_type = 'payments'

        # Construir endpoint
        endpoint = (
            f"{base_url}{recurse}/{payment_type}/{transaction_id}/cancellations"
            f"?cuit_cuil={cuit_cuil}&subnet_acquirer_id={subnet_acquirer_id}"
        )
        _logger.info('PUT CANCELLATION REQUEST URL: %s', endpoint)

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }

        try:
            response = requests.put(endpoint, headers=headers, timeout=10)
            # Registrar log
            self.env['payway.log'].sudo().create_logs(
                pos_session,
                'remove_order',
                headers,
                endpoint,
                response.status_code,
                '',
                ''
            )
            if response.status_code == 200:
                data = response.json()
                _logger.info('CANCELATION RESPONSE: %s', data)

                # Extraer el estado según el tipo de operación
                status = None
                if payment_type == 'reversals' and 'reversal_data' in data:
                    status = data['reversal_data'].get('reversal_status')
                elif payment_type == 'refunds' and 'refund_data' in data:
                    status = data['refund_data'].get('refund_status')
                elif payment_type == 'payments' and 'payment_data' in data:
                    status = data['payment_data'].get('payment_status')

                if status:
                    return {
                        'status_code': 200,
                        'cancellation_status': status
                    }
                else:
                    return {
                        'status_code': 400,
                        'error': 'No cancellation status found in response'
                    }
            else:
                error_msg = response.json().get('errors', [{'title': 'Unknown error'}])[0].get('title', 'Unknown error')
                _logger.error('Cancellation error: %s', error_msg)
                return {
                    'status_code': response.status_code,
                    'error': error_msg
                }

        except requests.exceptions.RequestException as e:
            _logger.exception('Request error during cancellation: %s', str(e))
            return {
                'status_code': 500,
                'error': str(e)
            }

    def payway_updating_order(self, order):
        pos_order_id = self.env['pos.order'].search([('access_token', '=', order['access_token_order'])])
        pos_order_id.write({'payway_payment_token': order['access_token_payment']})
        return True

    def payway_payment_status(self, order):
        # Buscar sesión POS
        pos_session = self.env['pos.session'].browse(order['pos_session_id'])
        if not pos_session:
            return {'status_code': 404, 'error': 'POS session not found'}

        # Validar y actualizar token si es necesario
        pos_session.config_id._ensure_valid_token()

        # Obtener método de pago
        payment_method = self.env['pos.payment.method'].browse(order['payment_method_id'])
        if not payment_method:
            return {'status_code': 404, 'error': 'Payment method not found'}

        # Determinar ambiente (test o producción)
        base_url = TEST_BASE_API_URL if payment_method.payway_test_mode else PROD_BASE_API_URL

        # Datos de la solicitud
        access_token = pos_session.config_id.access_token or ''
        cuit_cuil = payment_method.company_id.vat
        subnet_acquirer_id = payment_method.pos_payway_config_id.payway_acquier_id
        transaction_id = order.get("access_token_payment")

        # Mapeo de tipos de pago
        payment_type = order['payment_type_build']
        if payment_type == 'reversals_refunds':
            if payment_method.card_brand == 'AMEX':
                recurse = BASE_PATH_REFUNDS
                payment_type = 'refunds'
            else:
                recurse = BASE_PATH_REVERSAL
                payment_type = 'reversals'
        else:
            recurse = BASE_PATH_PAYMENT
            payment_type = 'payments'

        # Construir endpoint
        endpoint = (
            f"{base_url}{recurse}/{payment_type}/{transaction_id}"
            f"?cuit_cuil={cuit_cuil}&subnet_acquirer_id={subnet_acquirer_id}"
        )

        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}

        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            # Registrar log
            log_id = self.env['payway.log'].sudo().create_logs(
                pos_session,
                'get_order',
                headers,
                endpoint,
                response.status_code,
                '',
                response.json() if response.content else ''
            )
            log_id.write({'payment_id': transaction_id})
            if response.status_code == 200:
                data = response.json()

                status = None
                if payment_type == 'reversals' and 'reversal_data' in data:
                    status = data['reversal_data'].get('reversal_status')
                elif payment_type == 'refunds' and 'refund_data' in data:
                    status = data['refund_data'].get('refund_status')
                elif payment_type == 'payments' and 'payment_data' in data:
                    status = data['payment_data'].get('payment_status')

                if status:
                    return {
                        'status_code': 200,
                        'payment_status': status
                    }
                else:
                    return {
                        'status_code': 400,
                        'error': 'No status found in response'
                    }
            else:
                error_msg = response.json().get('errors', [{'title': 'Unknown error'}])[0]['title']
                
                return {
                    'status_code': response.status_code,
                    'error': error_msg
                }

        except requests.exceptions.RequestException as e:
            _logger.exception('Request error occurred: %s', str(e))
            return {
                'status_code': 500,
                'error': str(e)
            }

    def payway_make_refunds(self, orders):
        # Obtener sesión POS y orden original
        pos_session_id = self.env['pos.session'].browse(orders['pos_session_id'])
        pos_order_id = self.env['pos.order'].browse(orders['original_pos_order_id'])

        # Validar que los registros existan
        if not pos_session_id or not pos_order_id:
            return {'status_code': 404, 'error': 'POS session or order not found'}

        # Obtener método de pago
        pos_payment_method_id = self.env['pos.payment.method'].browse(orders['payment_method_id'])
        if not pos_payment_method_id:
            return {'status_code': 404, 'error': 'Payment method not found'}

        # Validar y actualizar token si es necesario
        pos_session_id.config_id._ensure_valid_token()

        # Determinar entorno (test/prod)
        url = TEST_BASE_API_URL if pos_payment_method_id.payway_test_mode else PROD_BASE_API_URL

        # Datos de autenticación y empresa
        access_token = pos_session_id.config_id.access_token or ''
        subnet_acquirer_id = pos_payment_method_id.pos_payway_config_id.payway_acquier_id
        cuit_cuil = pos_payment_method_id.company_id.vat

        # Validar CUIT/CUIL
        if not cuit_cuil:
            return {'status_code': 400, 'error': 'Missing CUIT/CUIL'}

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }

        # Preparar monto
        amount_total = float(orders['amount_total'])
        amount_return = round(abs(amount_total), 2)
        amount_total_str = f"{int(amount_return):03d}{int(round((amount_return - int(amount_return)) * 100)):02d}"

        # Procesar según marca de tarjeta
        if pos_payment_method_id.card_brand == 'AMEX':
            # Refund (AMEX)
            endpoint = f"{url}{BASE_PATH_REFUNDS}/refunds?cuit_cuil={cuit_cuil}"
            payload = {
                "subnet_acquirer_id": subnet_acquirer_id,
                "refund_amount": amount_total_str,
                "terminal_menu_text": f"Devolución NR ${amount_return}",
                "ecr_provider": pos_payment_method_id.company_id.name,
                "ecr_name": pos_payment_method_id.company_id.name,
                "ecr_version": "1.0",
                "ecr_transaction_id": None,
                "print_copies": "BOTH",
                "terminals_list": [
                    {"terminal_id": pos_payment_method_id.payway_terminal_number}
                ],
                "card_brand_product": None
            }

            try:
                response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
                # Registrar log
                self.env['payway.log'].sudo().create_logs(
                    pos_order_id.session_id,
                    'refund_order',
                    headers,
                    endpoint,
                    response.status_code,
                    '',
                    response.json() if response.content else ''
                )
                if response.status_code == 200:
                    data = response.json()
                    refund_id = data['refund_data']['refund_id']
                    return {'status_code': 200, 'transaction_id': refund_id}
                else:
                    error_msg = response.json().get('errors', [{}])[0].get('title', 'Unknown error')
                    return {'status_code': response.status_code, 'error': error_msg}
            except requests.RequestException as e:
                _logger.exception("Error connecting to Payway refund API")
                return {'status_code': 500, 'error': str(e)}

        else:
            # Reversal (otras tarjetas)
            if not pos_order_id.payway_payment_token:
                return {'status_code': 400, 'error': 'Missing Payway payment token'}

            endpoint = f"{url}{BASE_PATH_REVERSAL}/reversals?cuit_cuil={cuit_cuil}"
            payload = {
                "reversal_request_data": {
                    "subnet_acquirer_id": subnet_acquirer_id,
                    "payment_id": pos_order_id.payway_payment_token,
                    "terminal_menu_text": f"Pedido de ${amount_return}",
                    "ecr_transaction_id": None,
                    "print_copies": 2,
                    "terminals_list": [
                        {"terminal_id": pos_payment_method_id.payway_terminal_number}
                    ],
                }
            }

            try:
                response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    payment_id = data['reversal_data']['payment_id']
                    return {'status_code': 200, 'transaction_id': payment_id}
                else:
                    error_msg = response.json().get('errors', [{}])[0].get('title', 'Unknown error')
                    return {'status_code': response.status_code, 'error': error_msg}
            except requests.RequestException as e:
                _logger.exception("Error connecting to Payway reversal API")
                return {'status_code': 500, 'error': str(e)}
