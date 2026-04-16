from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    last_purchase_price = fields.Float(
        string="Last Bill Price",
        compute="_compute_last_purchase_price",
        store=False
    )

    @api.depends('product_id', 'order_id.partner_id')
    def _compute_last_purchase_price(self):
        """Compute the last purchase price for the same vendor and product"""
        for line in self:
            last_price = 0.0
            partner = line.order_id.partner_id
            product = line.product_id

            if partner and product:
                # 🔍 Find latest previous confirmed/done purchase orders
                prev_orders = self.env['purchase.order'].search([
                    ('partner_id', '=', partner.id),
                    ('state', 'in', ['purchase', 'done']),
                    ('id', '!=', line.order_id.id)
                ], order='date_order desc', limit=5)

                # Search lines in those orders for this product
                prev_line = self.env['purchase.order.line'].search([
                    ('order_id', 'in', prev_orders.ids),
                    ('product_id', '=', product.id)
                ], order='id desc', limit=1)

                if prev_line:
                    last_price = prev_line.price_unit

            line.last_purchase_price = last_price
