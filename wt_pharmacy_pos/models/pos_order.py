# -*- coding: utf-8 -*-
from odoo import models, fields, api

class PosOrder(models.Model):
	_inherit = 'pos.order'

	prescription_id = fields.Many2one('pharmacy.prescription', string='Prescription', readonly=True, copy=False)

	@api.model
	def _process_order(self, order, existing_order):
		"""When the order is processed, dispense the linked prescription."""
		order_id = super()._process_order(order, existing_order)
		if order.get('prescription_id'):
			prescription = self.env['pharmacy.prescription'].browse(order.get('prescription_id'))
			if prescription.exists():
				prescription.action_dispense()
		return order_id