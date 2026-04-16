# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_default_customer_screen = fields.Boolean(related="pos_config_id.pos_default_customer_screen", readonly=False)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    pos_default_customer_screen = fields.Boolean(string="Open Default Customer Screen")
