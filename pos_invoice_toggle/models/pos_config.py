from odoo import fields, models

class PosConfig(models.Model):
    _inherit = "pos.config"

    hide_pos_invoice_button = fields.Boolean(
        string="Hide POS Invoice Button",
        help="Enable this option to hide the Invoice button on the Payment Screen."
    )
