# -*- coding: utf-8 -*-

from odoo import fields, models

class PosConfig(models.Model):
    _inherit = 'pos.config'

    pos_hide_product_info = fields.Boolean(
        string="Hide Product 'Info' Button"
    )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_hide_product_info = fields.Boolean(
        string="Hide Product 'Info' Button",
        related="pos_config_id.pos_hide_product_info",
        readonly=False,
        help="This will allow hiding the product 'Info' button from the Point of Sale screen."
    )
