# -*- coding: utf-8 -*-
from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_medicine = fields.Boolean(string="Is a Medicine", help="Check this box if the product is a medicine.")
    is_prescription_drug = fields.Boolean(string='Requires Prescription', default=False, help="Check this box if this medicine requires a prescription to be sold.")
    manufacturer = fields.Char(string='Manufacturer')
    dosage_form = fields.Char(string='Dosage Form', help="e.g., Tablet, Syrup, Injection")
    strength = fields.Char(string='Strength', help="e.g., 500mg, 10ml")