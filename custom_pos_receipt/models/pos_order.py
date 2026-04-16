# -*- coding: utf-8 -*-

from odoo import fields, models, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def get_invoice_name(self):
        return self.account_move.name

    @api.model
    def get_invoice_number(self, order_name):
        order = self.search([("pos_reference", "=", order_name)], limit=1)
        if order and order.account_move:
            return order.account_move.name
        return False
