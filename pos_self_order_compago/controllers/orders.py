from odoo import http
from odoo.addons.pos_self_order.controllers.orders import PosSelfOrderController
from werkzeug.exceptions import Unauthorized


class PosSelfOrderControllerRazorpay(PosSelfOrderController):
    @http.route('/pos-self-order/compago-payment-intent-status', auth='public', type='json', website=True)
    def compago_payment_intent_status(self, access_token, order_access_token, payment_intent_id, payment_method_id):
        pos_config = self._verify_pos_config(access_token)
        order = pos_config.env['pos.order'].search([
            ('access_token', '=', order_access_token),
            ('config_id', '=', pos_config.id)
        ])

        if not order:
            raise Unauthorized()

        payment_method = pos_config.env['pos.payment.method'].browse(payment_method_id)
        payment_intent_response = payment_method.compago_get_payment_intent_status(payment_intent_id)

        payment_intent_expired = payment_intent_response.get('expired')
        payment_intent_status = payment_intent_response.get('status')

        payment_summary = payment_intent_response.get('paymentSummary', {})
        payment_status = payment_summary.get('status')

        if payment_status == 'SUCCESS':
            payment = payment_summary.get('payment', {})
            payment_transaction = payment_summary.get('paymentTransaction', {})
            card_information = payment_summary.get('cardInformation', {})

            order.add_payment({
                'amount': order.amount_total,
                'payment_method_id': payment_method.id,
                'card_type': card_information.get('fundingSource'),
                'card_brand': card_information.get('networkType'),
                'card_no': card_information.get('lastFourDigits'),
                'cardholder_name': '',
                'transaction_id': payment.get('id'),
                'payment_status': payment_intent_status,
                'pos_order_id': order.id,
                'payment_method_authcode': payment_transaction.get('resultCode'),
                'payment_method_issuer_bank': card_information.get('issuingBank'),
                'payment_method_payment_mode': card_information.get('entryMode'),
                'payment_ref_no': payment.get('operationCode'),
            })

            order.action_pos_order_paid()

            if order.config_id.self_ordering_mode == 'kiosk':
                self._notify_payment_result(order, 'Success')

            return {'status': 'CONFIRMED'}
        elif payment_intent_expired == True or payment_intent_status == 'CANCELLED':
            self._notify_payment_result(order, 'fail')
            return {'status': 'FAILED'}

        return {'status': 'PENDING'}

    @http.route('/pos-self-order/compago-cancel-payment-intent', auth='public', type='json', website=True)
    def compago_cancel_payment_intent(self, access_token, order_access_token, payment_intent_id, payment_method_id):
        pos_config = self._verify_pos_config(access_token)
        order = pos_config.env['pos.order'].search([
            ('access_token', '=', order_access_token),
            ('config_id', '=', pos_config.id)
        ])

        if not order:
            raise Unauthorized()

        payment_method = pos_config.env['pos.payment.method'].browse(payment_method_id)
        payment_intent_cancellation = payment_method.compago_cancel_payment_intent(payment_intent_id)

        self._notify_payment_result(order, 'fail')
        return payment_intent_cancellation

    def _notify_payment_result(self, order, payment_result):
        order.config_id._notify('PAYMENT_STATUS', {
            'payment_result': payment_result,
            'data': {
                'pos.order': order.read(order._load_pos_self_data_fields(order.config_id.id), load=False),
                'pos.order.line': order.lines.read(order._load_pos_self_data_fields(order.config_id.id), load=False),
            }
        })
