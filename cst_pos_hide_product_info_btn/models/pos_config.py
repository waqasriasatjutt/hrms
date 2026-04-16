# -*- coding: utf-8 -*-

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    hide_product_info = fields.Boolean(string="Hide Product 'Info' Button",
                                       help="If enabled, the 'i' button showing product details will be hidden in the POS interface for this configuration.")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_hide_product_info = fields.Boolean(string="Hide Product Info(i)", related="pos_config_id.hide_product_info",
                                           readonly=False)
