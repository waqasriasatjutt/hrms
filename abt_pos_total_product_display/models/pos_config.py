# -*- coding: utf-8 -*-

from odoo import  api, fields, models

class PosConfig(models.Model):
    _inherit = "pos.config"

    display_category_product_count = fields.Boolean(
        string="Display Number of Products in Category",
        help="If checked, the total number of products within the current category will be shown on the screen."
    )
    primary_color_code = fields.Char(
        string="Primary Color Code", 
        help="The hexadecimal or RGB color code for the primary color."
    )
    your_label = fields.Char(
        string="Label", translate=True, 
        help="A user-friendly label for the color, translated into the user's language."
    )
