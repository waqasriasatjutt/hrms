# -*- coding: utf-8 -*-

from odoo import api, models, _

class HrEmployee(models.Model):
	_inherit = 'hr.employee'

	def _load_pos_data(self, data):
		result = super()._load_pos_data(data)
		config_id = self.env['pos.config'].browse(data['pos.config']['data'][0]['id'])
		
		restrict_quantity_employee_ids = config_id.restrict_quantity_employee_ids.ids
		restrict_discount_employee_ids = config_id.restrict_discount_employee_ids.ids
		restrict_price_employee_ids = config_id.restrict_price_employee_ids.ids
		restrict_remove_line_employee_ids = config_id.restrict_remove_line_employee_ids.ids
		restrict_plus_minus_employee_ids = config_id.restrict_plus_minus_employee_ids.ids
		restrict_cancel_order_employee_ids = config_id.restrict_cancel_order_employee_ids.ids
		restrict_cash_in_out_employee_ids = config_id.restrict_cash_in_out_employee_ids.ids
		restrict_refund_employee_ids = config_id.restrict_refund_employee_ids.ids

		for employee in result.get('data'):
			if employee.get('id'):
				employee['_is_restrict_quantity'] = employee.get('id') in restrict_quantity_employee_ids
				employee['_is_restrict_discount'] = employee.get('id') in restrict_discount_employee_ids
				employee['_is_restrict_price'] = employee.get('id') in restrict_price_employee_ids
				employee['_is_restrict_remove_line'] = employee.get('id') in restrict_remove_line_employee_ids
				employee['_is_restrict_plus_minus'] = employee.get('id') in restrict_plus_minus_employee_ids
				employee['_is_restrict_cancel_order'] = employee.get('id') in restrict_cancel_order_employee_ids
				employee['_is_restrict_cash_in_out'] = employee.get('id') in restrict_cash_in_out_employee_ids
				employee['_is_restrict_refund_order'] = employee.get('id') in restrict_refund_employee_ids

		return result