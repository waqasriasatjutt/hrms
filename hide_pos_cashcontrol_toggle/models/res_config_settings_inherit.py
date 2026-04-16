from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    hide_opening_cash_control = fields.Boolean(
        string="Hide Opening Cash Control in POS",
        related='pos_config_id.hide_opening_cash_control',
        readonly=False,
    )

    

