from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_stock_alert = fields.Boolean(
        string="Low Stock Alert",
        config_parameter='product_stock_low_alert.enable_alert',
        help="Enable visual alerts when product stock goes below a threshold."
    )

    min_stock_alert_qty = fields.Integer(
        string='Alert Quantity',
        default=0,
        config_parameter='product_stock_low_alert.min_alert_qty',
        help="Minimum stock quantity to trigger alert."
    )
