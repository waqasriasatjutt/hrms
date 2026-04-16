from odoo import fields, models


class PosConfigSettings(models.TransientModel):
    """Class for adding custom fields in res.config.settings for POS"""
    _inherit = 'res.config.settings'

    show_total_items = fields.Boolean(
        string="Enable Show Total Items",
        related="pos_config_id.show_total_items",
        help="Enabling this option will display the total number of items and "
             "the total quantity of products on the PoS screen.",
        readonly=False
    )
    show_total_quantity = fields.Boolean(
        string="Enable Show Total Quantity",
        related="pos_config_id.show_total_quantity",
        help="Enabling this option will display the total number of items and "
             "the total quantity of products on the receipt.",
        readonly=False
    )
