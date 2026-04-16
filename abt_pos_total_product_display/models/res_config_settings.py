# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    display_category_product_count = fields.Boolean(
        string="Display Number of Products in Category", 
        related="pos_config_id.display_category_product_count", readonly=False
    )
    primary_color_code = fields.Char(
        string="String Color",related="pos_config_id.primary_color_code", readonly=False
    )
    your_label = fields.Char(
        string="Label",related="pos_config_id.your_label",translate=True,readonly=False
    )
