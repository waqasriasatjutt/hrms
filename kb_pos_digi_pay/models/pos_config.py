# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    digipay_ecommerce_token = fields.Char(string='DigiPay Ecommerce Token', readonly=False)


class PosOrderInherit(models.Model):
    _inherit = "pos.order"

    @api.model
    def _payment_fields(self, order, ui_paymentline):
        fields = super(PosOrderInherit, self)._payment_fields(order, ui_paymentline)

        fields.update({
            'is_digipay': ui_paymentline.get('is_digipay'),
            'digipay_status': ui_paymentline.get('digipay_status'),
            'digipay_db_ref_no': ui_paymentline.get('digipay_db_ref_no'),
            'digipay_textresponse': ui_paymentline.get('digipay_textresponse'),
            'digipay_resp_code': ui_paymentline.get('digipay_resp_code'),
            'digipay_terminal_id': ui_paymentline.get('digipay_terminal_id'),
            'digipay_approval_code': ui_paymentline.get('digipay_approval_code'),
            'digipay_payment_request_id': ui_paymentline.get('digipay_payment_request_id'),
            'digipay_rrn': ui_paymentline.get('digipay_rrn'),
        })

        return fields


class PosPaymentInherit(models.Model):
    _inherit = 'pos.payment'

    is_digipay = fields.Boolean('Is DigiPay', default=False)
    digipay_status = fields.Char('DigiPay status')
    digipay_db_ref_no = fields.Char('DigiPay db ref no')
    digipay_textresponse = fields.Char('DigiPay resp text')
    digipay_resp_code = fields.Char('Resp code')
    digipay_terminal_id = fields.Char('DigiPay terminal ID')
    digipay_approval_code = fields.Char('DigiPay auth code')
    digipay_payment_request_id = fields.Char('DigiPay req')
    digipay_rrn = fields.Char('DigiPay RRN')