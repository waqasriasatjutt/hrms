# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _

class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    digi_pay_identifier = fields.Char(help='[Terminal model]-[Serial number]', copy=False)
    is_digipay_test_mode = fields.Boolean(string='Active DigiPay test mode', default=False)

    # add DigiPay 
    def _get_payment_terminal_selection(self):
        return super(PosPaymentMethod, self)._get_payment_terminal_selection() + [('digi_pay', 'DigiPay')]
