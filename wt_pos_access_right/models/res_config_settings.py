# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, Command

class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	pos_restrict_quantity_employee_ids = fields.Many2many(
		related='pos_config_id.restrict_quantity_employee_ids',
		relation='restrict_qty_employee_res_config_settings_rel', 
		string="Restrict Quantity Control",
		help='employees can not access quantity button',
		readonly=False)
	pos_restrict_discount_employee_ids = fields.Many2many(
		related='pos_config_id.restrict_discount_employee_ids',
		relation='restrict_discount_employee_res_config_settings_rel', 
		string="Restrict Discount Control",
		help='employees can not access discount button',
		readonly=False)
	pos_restrict_price_employee_ids = fields.Many2many(
		related='pos_config_id.restrict_price_employee_ids',
		relation='restrict_price_employee_res_config_settings_rel', 
		string="Restrict Price Control",
		help='employees can not access price button',
		readonly=False)
	pos_restrict_remove_line_employee_ids = fields.Many2many(
		related='pos_config_id.restrict_remove_line_employee_ids',
		relation='restrict_remove_line_employee_res_config_settings_rel', 
		string="Restrict Remove Line Control",
		help='Employees can not access Remove Line button',
		readonly=False)
	pos_restrict_plus_minus_employee_ids = fields.Many2many(
		related='pos_config_id.restrict_plus_minus_employee_ids',
		relation='restrict_plu_min_employee_res_config_settings_rel', 
		string="Restrict +/- Control",
		help='employees can not access plus-minus (+/-) button',
		readonly=False)

	pos_restrict_cancel_order_employee_ids = fields.Many2many(
		related='pos_config_id.restrict_cancel_order_employee_ids',
		relation='restrict_cancel_order_employee_res_config_settings_rel', 
		string="Restrict Cancel Order Control",
		help='employees can not access cancel order button',
		readonly=False)
	pos_restrict_cash_in_out_employee_ids = fields.Many2many(
		related='pos_config_id.restrict_cash_in_out_employee_ids', 
		relation='restrict_cash_in_out_employee_res_config_settings_rel', 
		string="Restrict Cash In-Out Control",
		help='Employees can not access Cash In-Out button',
		readonly=False)
	pos_restrict_refund_employee_ids = fields.Many2many(
		related='pos_config_id.restrict_refund_employee_ids',
		relation='restrict_refund_employee_pos_config_rel', 
		string="Restrict Refund Order Control",
		help='Employees can not access refund oredr',
		readonly=False)

	@api.onchange('pos_basic_employee_ids','pos_advanced_employee_ids')
	def _onchange_pos_restrict_access_employee_ids(self):
		config_employee_ids = self.pos_basic_employee_ids + self.pos_advanced_employee_ids
		
		pos_restrict_quantity_employee_ids = self.pos_restrict_quantity_employee_ids
		for employee in pos_restrict_quantity_employee_ids:
			if employee not in config_employee_ids:
				self.pos_restrict_quantity_employee_ids -= employee

		pos_restrict_discount_employee_ids = self.pos_restrict_discount_employee_ids
		for employee in pos_restrict_discount_employee_ids:
			if employee not in config_employee_ids:
				self.pos_restrict_discount_employee_ids -= employee

		pos_restrict_price_employee_ids = self.pos_restrict_price_employee_ids
		for employee in pos_restrict_price_employee_ids:
			if employee not in config_employee_ids:
				self.pos_restrict_price_employee_ids -= employee

		pos_restrict_remove_line_employee_ids = self.pos_restrict_remove_line_employee_ids
		for employee in pos_restrict_remove_line_employee_ids:
			if employee not in config_employee_ids:
				self.pos_restrict_remove_line_employee_ids -= employee

		pos_restrict_plus_minus_employee_ids = self.pos_restrict_plus_minus_employee_ids
		for employee in pos_restrict_plus_minus_employee_ids:
			if employee not in config_employee_ids:
				self.pos_restrict_plus_minus_employee_ids -= employee

		pos_restrict_cancel_order_employee_ids = self.pos_restrict_cancel_order_employee_ids
		for employee in pos_restrict_cancel_order_employee_ids:
			if employee not in config_employee_ids:
				self.pos_restrict_cancel_order_employee_ids -= employee

		pos_restrict_cash_in_out_employee_ids = self.pos_restrict_cash_in_out_employee_ids
		for employee in pos_restrict_cash_in_out_employee_ids:
			if employee not in config_employee_ids:
				self.pos_restrict_cash_in_out_employee_ids -= employee

		pos_restrict_refund_employee_ids = self.pos_restrict_refund_employee_ids
		for employee in pos_restrict_refund_employee_ids:
			if employee not in config_employee_ids:
				self.pos_restrict_refund_employee_ids -= employee

				

				