# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class PosConfig(models.Model):
    _inherit = 'pos.config'


    dual_currency_rate = fields.Float(string="USD → LBP Rate", default=89000)
