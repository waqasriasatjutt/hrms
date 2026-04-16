from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    low_stock_label = fields.Char(
        string='Low Stock Label',
        compute='_compute_low_stock_label',
        help='Shows remaining quantity when product stock is low.'
    )

    @api.depends('qty_available')
    def _compute_low_stock_label(self):
        alert_enabled = self.env['ir.config_parameter'].sudo().get_param(
            'product_stock_low_alert.enable_alert'
        )
        min_qty = int(
            self.env['ir.config_parameter'].sudo().get_param(
                'product_stock_low_alert.min_alert_qty', 0
            )
        )

        for product in self:
            if alert_enabled and product.is_storable and product.qty_available <= min_qty:
                product.low_stock_label = product.qty_available
            else:
                product.low_stock_label = False

    @api.model
    def _load_pos_data_fields(self, config_id):
        fields_list = super()._load_pos_data_fields(config_id)
        fields_list.append('low_stock_label')
        return fields_list
