# -*- coding: utf-8 -*-

from odoo import models, fields


class POSConfig(models.Model):
    _inherit = 'pos.config'

    user_ids = fields.Many2many('res.users',)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_user_ids = fields.Many2many(related="pos_config_id.user_ids", readonly=False,)
