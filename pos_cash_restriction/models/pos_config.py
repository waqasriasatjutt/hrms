# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_cash_restriction = fields.Boolean(
        string="Enable Cash Restriction",
        default=True,
        help="If enabled, restricts cash withdrawals to the available amount in the cash register."
    )
    
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    pos_enable_cash_restriction = fields.Boolean(related='pos_config_id.enable_cash_restriction',readonly=False)

