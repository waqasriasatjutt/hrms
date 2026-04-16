# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SBLPosConfig(models.Model):
    _inherit = 'pos.config'

    sbl_enable_pos_speedup = fields.Boolean(
        string="Enable POS Speedup",
        default=False,
        help="Enable smart loading with configurable limits and dynamic search for improved performance"
    )
    sbl_initial_product_limit = fields.Integer(
        string="Initial Product Limit",
        default=1000,
        help="Number of products to load initially when POS starts. Products marked as 'Always Load' are included in addition to this limit."
    )
    sbl_initial_customer_limit = fields.Integer(
        string="Initial Customer Limit", 
        default=50,
        help="Number of customers to load initially when POS starts. Customers marked as 'Always Load' are included in addition to this limit."
    )

    @api.constrains('sbl_initial_product_limit', 'sbl_initial_customer_limit')
    def _check_speedup_limits(self):
        for config in self:
            if config.sbl_enable_pos_speedup:
                if config.sbl_initial_product_limit < 1:
                    raise ValueError(_("Initial Product Limit must be at least 1"))
                if config.sbl_initial_customer_limit < 1:
                    raise ValueError(_("Initial Customer Limit must be at least 1"))
                if config.sbl_initial_product_limit > 50000:
                    raise ValueError(_("Initial Product Limit should not exceed 50,000 for performance reasons"))
                if config.sbl_initial_customer_limit > 10000:
                    raise ValueError(_("Initial Customer Limit should not exceed 10,000 for performance reasons"))

    def get_limited_product_count(self):
        """Override core method to use per-POS limits when speedup is enabled"""
        if self.sbl_enable_pos_speedup:
            return self.sbl_initial_product_limit
        return super().get_limited_product_count()

    def _get_limited_partner_count(self):
        """Override core method to use per-POS limits when speedup is enabled"""
        if self.sbl_enable_pos_speedup:
            return self.sbl_initial_customer_limit
        return super()._get_limited_partner_count()

    def sbl_get_speedup_config(self):
        """Return speedup configuration for frontend"""
        return {
            'enabled': self.sbl_enable_pos_speedup,
            'product_limit': self.sbl_initial_product_limit,
            'customer_limit': self.sbl_initial_customer_limit,
        }