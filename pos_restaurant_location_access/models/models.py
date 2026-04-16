# -*- coding: utf-8 -*-
from odoo import api, fields, models

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    floor_ids = fields.Many2many('restaurant.floor', string="POS Floors")

    @api.model
    def _load_pos_data_fields(self, config_id):
        result = super()._load_pos_data_fields(config_id)
        if 'floor_ids' not in result:
            result.append('floor_ids')
        return result


# class HrEmployee(models.Model):
# 	_inherit = 'hr.employee'

# 	floor_ids = fields.Many2many('restaurant.floor', string="POS Floors")
	
# class PosSession(models.Model):
# 	_inherit = "pos.session"

# 	def _loader_params_hr_employee(self):
# 		result = super()._loader_params_hr_employee()
# 		result['search_params']['fields'].append('floor_ids')
# 		return result