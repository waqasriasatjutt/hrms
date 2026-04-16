# Powered by Sensible Consulting Services
# -*- coding: utf-8 -*-
# © 2025 Sensible Consulting Services (<https://sensiblecs.com/>)
from odoo import Command, _, api, fields, models


class POSOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def sync_from_ui(self, orders):
        remaining_orders = []
        for index, order in enumerate(orders):
            pos_session = self.env['pos.session'].browse(order['session_id'])
            if not pos_session or not pos_session.config_id or not pos_session.config_id.sbl_create_sale_order:
                remaining_orders.append(order)
            else:
                self.env['sale.order'].sbl_create_order_from_pos(
                    order,
                    pos_session.id,
                    action=pos_session.config_id.sbl_create_sale_order_action,
                )
        return super().sync_from_ui(remaining_orders)