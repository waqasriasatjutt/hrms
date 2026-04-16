from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    low_stock_active = fields.Boolean(
        string='Low Stock Active',
        compute='_compute_low_stock_active'
    )

    low_stock_bg_color = fields.Char(
        string='Low Stock Background Color'
    )

    low_stock_label_display = fields.Char(
        string='Low Stock Label',
        compute='_compute_low_stock_label_display'
    )

    @api.depends('low_stock_active')
    def _compute_low_stock_label_display(self):
        for rec in self:
            rec.low_stock_label_display = "⚠ LOW STOCK" if rec.low_stock_active else ""

    @api.depends('qty_available')
    def _compute_low_stock_active(self):
        alert_enabled = self.env['ir.config_parameter'].sudo().get_param(
            'product_stock_low_alert.enable_alert'
        )
        min_qty = int(
            self.env['ir.config_parameter'].sudo().get_param(
                'product_stock_low_alert.min_alert_qty', 0
            )
        )

        for template in self:
            if alert_enabled and template.is_storable and template.qty_available <= min_qty:
                template.low_stock_active = True
                template.low_stock_bg_color = '#ffcccc'  # 🔴 proper red tone
            else:
                template.low_stock_active = False
                template.low_stock_bg_color = '#ffffff'
