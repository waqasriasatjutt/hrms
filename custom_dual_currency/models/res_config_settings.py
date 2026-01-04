# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    dual_currency_rate = fields.Float(related='pos_config_id.dual_currency_rate',
        string="USD → LBP Rate",readonly=False)

