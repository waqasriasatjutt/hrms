from odoo import fields, models


class PosConfiguration(models.Model):
    """ Class for adding custom fields in the POS configuration """
    _inherit = "pos.config"

    show_total_items = fields.Boolean(
        help="Boolean field in pos.config corresponding to total_items in res.config.settings",
        string="Show Total Items"
    )
    show_total_quantity = fields.Boolean(
        help="Boolean field in pos.config corresponding to total_quantity in res.config.settings",
        string="Show Total Quantity"
    )
