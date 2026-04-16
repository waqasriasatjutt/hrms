# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from datetime import datetime
import json


class PosOrder(models.Model):
    _inherit = 'pos.order'

    payment_status = fields.Char('Payment Status')
    dojo_transaction_data = fields.Char()
    dojo_transaction_ids = fields.One2many(
        comodel_name='dojo.transaction',
        inverse_name='order_id',
        string='Dojo Transactions'
    )

    @api.model
    def sync_from_ui(self, orders):
        # EXTENDS 'point_of_sale'
        for order in orders:
            if order.get('dojo_transaction_data'):
                dojo_transaction_data = json.loads(order.get('dojo_transaction_data'))
                original_datetime = datetime.strptime(dojo_transaction_data['transactionTime'], '%Y-%m-%dT%H:%M:%S')
                dojo_transaction_data['transactionTime'] = original_datetime.strftime('%Y-%m-%d %H:%M:%S')
                order['dojo_transaction_ids'] = [(0, 0, dojo_transaction_data)]

        return super().sync_from_ui(orders)
