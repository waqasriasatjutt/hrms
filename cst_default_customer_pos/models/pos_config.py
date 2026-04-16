# -*- coding: utf-8 -*-

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    default_customer = fields.Many2one('res.partner', string='Default Customer')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_default_customer = fields.Many2one('res.partner', related='pos_config_id.default_customer', readonly=False)
