# -*- coding: utf-8 -*-

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    show_sequence_number = fields.Boolean(string="Show Order Line Sequence Number",
                                          help="Enable this option to display a sequence number for each order line in the Point of Sale screen.")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_show_sequence_number = fields.Boolean(string="Show Order Line Sequence Number",
                                              related="pos_config_id.show_sequence_number", readonly=False)
