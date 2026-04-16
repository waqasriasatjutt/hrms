# -*- coding: utf-8 -*-

from odoo import fields, models

class PosConfig(models.Model):
    _inherit = 'pos.config'
    
    guard_duplicate_zero_payment_line = fields.Boolean(
        string="Guard Payment Lines with 0 Amount",
        default=True,
        help="Prevent adding a payment line with amount 0 if one already exists."
    )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    pos_guard_duplicate_zero_payment_line = fields.Boolean(
        related='pos_config_id.guard_duplicate_zero_payment_line',
        readonly=False
    )
