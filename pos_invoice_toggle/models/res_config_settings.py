from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    hide_pos_invoice_button = fields.Boolean(
        related="pos_config_id.hide_pos_invoice_button",
        readonly=False
    )
