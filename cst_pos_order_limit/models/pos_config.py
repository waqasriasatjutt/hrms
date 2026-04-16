# -*- coding: utf-8 -*-

from odoo import models, fields,api
from odoo.exceptions import ValidationError


class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_order_limit = fields.Boolean(string='Enable Order Limit', default=False,
                                        help='Enable limitation on number of orders that can be created')

    max_orders = fields.Integer(string='Maximum Orders', default=10,
                                help='Maximum number of orders that can be created in a single session')

    @api.constrains('max_orders')
    def _check_max_orders(self):
        for config in self:
            if config.enable_order_limit and config.max_orders <= 0:
                raise ValidationError("Maximum Orders must be at least 1.")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_enable_order_limit = fields.Boolean(related="pos_config_id.enable_order_limit", readonly=False)
    pos_max_orders = fields.Integer(related="pos_config_id.max_orders",
                                    readonly=False)
