# Powered by Sensible Consulting Services
# -*- coding: utf-8 -*-
# © 2025 Sensible Consulting Services (<https://sensiblecs.com/>)
from odoo import api, fields, models


class SblResUsers(models.Model):
    _inherit = 'res.users'

    sbl_allow_direct_login = fields.Boolean('Allow Direct Login')
    sbl_pos_config_id = fields.Many2one('pos.config', string='Default Pos Config')

    @api.model
    def _load_pos_data_fields(self, config_id):
        fields = super()._load_pos_data_fields(config_id)
        fields += ['sbl_pos_config_id']
        return fields