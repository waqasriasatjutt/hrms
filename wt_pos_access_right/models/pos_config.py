# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, Command

class PosConfig(models.Model):
	_inherit = 'pos.config'

	restrict_quantity_employee_ids = fields.Many2many(
		'hr.employee', 
		relation='restrict_qty_employee_pos_config_rel',
		string="Restrict Quantity Control",
		help='Employees can not access quantity button')
	restrict_discount_employee_ids = fields.Many2many(
		'hr.employee', 
		relation='restrict_discount_employee_pos_config_rel', 
		string="Restrict Discount Control",
		help='Employees can not access discount button')
	restrict_price_employee_ids = fields.Many2many(
		'hr.employee', 
		relation='restrict_price_employee_pos_config_rel', 
		string="Restrict Price Control",
		help='Employees can not access price button')
	restrict_remove_line_employee_ids = fields.Many2many(
		'hr.employee', 
		relation='restrict_remove_line_employee_pos_config_rel', 
		string="Restrict Remove Line Control",
		help='Employees can not access Remove Line button')
	restrict_plus_minus_employee_ids = fields.Many2many(
		'hr.employee', 
		relation='restrict_plu_min_employee_pos_config_rel', 
		string="Restrict +/- Control",
		help='Employees can not access plus-minus (+/-) button')

	restrict_cancel_order_employee_ids = fields.Many2many(
		'hr.employee', 
		relation='restrict_cancel_order_employee_pos_config_rel', 
		string="Restrict Cancel Order Control",
		help='Employees can not access cancel order button')
	restrict_cash_in_out_employee_ids = fields.Many2many(
		'hr.employee', 
		relation='restrict_cash_in_out_employee_pos_config_rel', 
		string="Restrict Cash In-Out Control",
		help='Employees can not access Cash In-Out button')
	restrict_refund_employee_ids = fields.Many2many(
		'hr.employee', 
		relation='restrict_refund_employee_pos_config_rel', 
		string="Restrict Refund Order Control",
		help='Employees can not access refund oredr')


	@api.onchange('basic_employee_ids','advanced_employee_ids')
	def _onchange_restrict_access_employee_ids(self):
		config_employee_ids = self.basic_employee_ids + self.advanced_employee_ids
		
		restrict_quantity_employee_ids = self.restrict_quantity_employee_ids
		for employee in restrict_quantity_employee_ids:
			if employee not in config_employee_ids:
				self.restrict_quantity_employee_ids -= employee

		restrict_discount_employee_ids = self.restrict_discount_employee_ids
		for employee in restrict_discount_employee_ids:
			if employee not in config_employee_ids:
				self.restrict_discount_employee_ids -= employee

		restrict_price_employee_ids = self.restrict_price_employee_ids
		for employee in restrict_price_employee_ids:
			if employee not in config_employee_ids:
				self.restrict_price_employee_ids -= employee

		restrict_remove_line_employee_ids = self.restrict_remove_line_employee_ids
		for employee in restrict_remove_line_employee_ids:
			if employee not in config_employee_ids:
				self.restrict_remove_line_employee_ids -= employee

		restrict_plus_minus_employee_ids = self.restrict_plus_minus_employee_ids
		for employee in restrict_plus_minus_employee_ids:
			if employee not in config_employee_ids:
				self.restrict_plus_minus_employee_ids -= employee

		restrict_cancel_order_employee_ids = self.restrict_cancel_order_employee_ids
		for employee in restrict_cancel_order_employee_ids:
			if employee not in config_employee_ids:
				self.restrict_cancel_order_employee_ids -= employee

		restrict_cash_in_out_employee_ids = self.restrict_cash_in_out_employee_ids
		for employee in restrict_cash_in_out_employee_ids:
			if employee not in config_employee_ids:
				self.restrict_cash_in_out_employee_ids -= employee

		restrict_refund_employee_ids = self.restrict_refund_employee_ids
		for employee in restrict_refund_employee_ids:
			if employee not in config_employee_ids:
				self.restrict_refund_employee_ids -= employee

				

				

				