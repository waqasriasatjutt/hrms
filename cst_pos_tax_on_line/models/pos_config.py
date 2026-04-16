# -*- coding: utf-8 -*-

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    order_line_tax = fields.Boolean(string="Show Tax per Order Line", default=False)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_order_line_tax = fields.Boolean(related="pos_config_id.order_line_tax", readonly=False,
                                        string="Show Tax per Order Line")
