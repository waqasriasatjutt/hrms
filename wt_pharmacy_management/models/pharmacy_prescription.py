# -*- coding: utf-8 -*-
from odoo import models, fields, api

class PharmacyPrescription(models.Model):
    _name = 'pharmacy.prescription'
    _description = 'Medical Prescription'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'prescription_date desc, id desc'

    name = fields.Char(string='Prescription ID', required=True, copy=False, readonly=True, default=lambda self: self.env['ir.sequence'].next_by_code('pharmacy.prescription'))
    patient_id = fields.Many2one('res.partner', string='Patient', required=True, domain="[('is_patient', '=', True)]", tracking=True)
    doctor_id = fields.Many2one('res.partner', string='Doctor', required=True, domain="[('is_doctor', '=', True)]", tracking=True)
    prescription_date = fields.Date(string='Date', default=fields.Date.context_today, tracking=True)
    prescription_line_ids = fields.One2many('pharmacy.prescription.line', 'prescription_id', string='Prescription Lines')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('dispensed', 'Dispensed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', readonly=True, tracking=True)
    sale_order_id = fields.Many2one('sale.order', string='Related Sale Order', readonly=True)

    def action_dispense(self):
        self.write({'state': 'dispensed'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

class PharmacyPrescriptionLine(models.Model):
    _name = 'pharmacy.prescription.line'
    _description = 'Prescription Line'

    prescription_id = fields.Many2one('pharmacy.prescription', string='Prescription Reference', required=True, ondelete='cascade')
    drug_id = fields.Many2one('product.product', string='Drug', required=True, domain="[('is_prescription_drug', '=', True)]")
    quantity = fields.Float(string='Quantity', default=1.0)
    dosage = fields.Char(string='Dosage', help="e.g., 1-0-1 After Food")
    notes = fields.Text(string='Notes')