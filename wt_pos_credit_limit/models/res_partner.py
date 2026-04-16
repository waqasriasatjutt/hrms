# Powered by Way4Tech
# -*- coding: utf-8 -*-
# © 2026 Way4Tech (<https://way4tech.com/>)

from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    available_credit = fields.Float('Available Credit', compute='_compute_available_credit', digits='Account')

    def _compute_available_credit(self):
        for partner in self:
            partner.available_credit = partner.credit_limit - partner.credit

    @api.model
    def _load_pos_data_fields(self, config_id):
        fields = super()._load_pos_data_fields(config_id)
        fields += ['available_credit', 'parent_id']
        return fields
    
    def get_available_credit(self):
        return self.available_credit