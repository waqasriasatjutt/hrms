from odoo import models, fields

class PosConfig(models.Model):
    _inherit = 'pos.config'

    hide_opening_cash_control = fields.Boolean(
        string="Hide Opening Cash Control"
    )
