# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class PosSessionInherit(models.Model):
    _inherit = 'pos.session'

    def _loader_params_pos_payment_method(self):
        result = super()._loader_params_pos_payment_method()
        result['search_params']['fields'].append('digi_pay_identifier')
        return result

    digipay_description = fields.Text(string='DigiPay description', readonly=True)
    digipay_sale_count = fields.Float(string='DigiPay sale_count', default=0, readonly=True)
    digipay_sale_total = fields.Float(string='DigiPay sale_total', default=0, readonly=True)
    digipay_void_count = fields.Float(string='DigiPay void_count', default=0, readonly=True)
    digipay_void_total = fields.Float(string='DigiPay void_total', default=0, readonly=True)

    def action_pos_session_closing_control(self):
        res = super(PosSessionInherit, self).action_pos_session_closing_control()
        digipay_model = self.env['digi.pay.integration']
        for session in self:
            resp = digipay_model.settlement_digipay(session.config_id.id, session.id)
        return res
