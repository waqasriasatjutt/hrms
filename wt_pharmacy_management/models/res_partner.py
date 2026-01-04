# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_patient = fields.Boolean(string='Is a Patient', default=False, help="Check this box if the contact is a patient.")
    is_doctor = fields.Boolean(string='Is a Doctor', default=False, help="Check this box if the contact is a doctor.")

    # Patient-specific fields
    patient_id = fields.Char(string='Patient ID', copy=False, readonly=True, tracking=True)
    date_of_birth = fields.Date(string='Date of Birth')
    age = fields.Integer(string='Age', compute='_compute_age', store=True, readonly=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')], string='Gender')

    # Doctor-specific fields
    license_id = fields.Char(string='Medical License ID')
    specialty = fields.Char(string='Specialty')

    @api.depends('date_of_birth')
    def _compute_age(self):
        """Computes age based on date of birth."""
        for record in self:
            if record.date_of_birth:
                today = date.today()
                record.age = today.year - record.date_of_birth.year - ((today.month, today.day) < (record.date_of_birth.month, record.date_of_birth.day))
            else:
                record.age = 0

    @api.model_create_multi
    def create(self, vals_list):
        """Assigns a unique Patient ID if the partner is a patient."""
        for vals in vals_list:
            if vals.get('is_patient') and not vals.get('patient_id'):
                vals['patient_id'] = self.env['ir.sequence'].next_by_code('pharmacy.patient') or 'New'
        return super().create(vals_list)