# -*- coding: utf-8 -*-
#
#  ┌────────────────────────────────────────────────────────────────────┐
#  │   Developed by: CHEF PIXEL                                         │
#  │   Website: https://chef-pixel.fr                                   │
#  │   Support: hello@chef-pixel.fr                                     │
#  │   Description: Add sequence numbers to POS order lines             │
#  └────────────────────────────────────────────────────────────────────┘
#
#  🔢 Improve readability and tracking in POS orders with line sequences!

from odoo import models, fields, api

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    sequence = fields.Char(string='Sequence', default=0)

    @api.model
    def _load_pos_data_fields(self, config_id):
        params = super()._load_pos_data_fields(config_id)
        params += ['sequence']
        return params