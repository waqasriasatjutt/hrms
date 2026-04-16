# Powered by Sensible Consulting Services
# -*- coding: utf-8 -*-
# © 2025 Sensible Consulting Services (<https://sensiblecs.com/>)
from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def _sbl_prepare_from_pos(self, sequence, order_line):
        order_line_data = order_line
        if isinstance(order_line, list):
            order_line_data = order_line[2]
        return {
            "sequence": sequence,
            "product_id": order_line_data["product_id"],
            "product_uom_qty": order_line_data["qty"],
            "discount": order_line_data["discount"],
            "price_unit": order_line_data["price_unit"],
            "tax_id": order_line_data["tax_ids"],
        }

    def _get_sale_order_line_multiline_description_sale(self):
        res = super()._get_sale_order_line_multiline_description_sale()

        for sequence, order_line in enumerate(
            self.env.context.get("pos_order_lines_data", []), start=1
        ):
            line_data = order_line
            if isinstance(order_line, list):
                line_data = order_line[2]
            if line_data.get("customer_note", False) and self.sequence == sequence:
                res += f"\n{line_data.get('customer_note')}"

        return res
