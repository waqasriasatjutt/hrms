# -*- coding: utf-8 -*-

from odoo import api, fields, models ,_
from odoo.exceptions import UserError
from datetime import datetime


class ACSPatient(models.Model):
    _name = 'hms.patient'
    _description = 'Patient'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'acs.hms.mixin']
    _inherits = {
        'res.partner': 'partner_id',
    }

    def _rec_count(self):
        Invoice = self.env['account.move']
        Prescription = self.env['prescription.order']
        Treatment = self.env['hms.treatment']
        Appointment = self.env['hms.appointment']
        for rec in self:
            rec.invoice_count = Invoice.search_count([('partner_id','=',rec.partner_id.id)])
            rec.prescription_count = Prescription.search_count([('patient_id','=',rec.id)])
            rec.treatment_count = Treatment.search_count([('patient_id','=',rec.id)])
            rec.appointment_count = Appointment.search_count([('patient_id','=',rec.id)])

    @api.model
    def _get_service_id(self):
        consultation = False
        if self.env.user.company_id.patient_registration_product_id:
            registration_product = self.env.user.company_id.patient_registration_product_id.id
        return registration_product

    cnic = fields.Char(String='CNIC')
    partner_id = fields.Many2one('res.partner', 'Partner', required=True, ondelete='restrict')
    gov_code = fields.Char(string='Government Identity')
    marital_status = fields.Selection([
        ('single', 'Single'), 
        ('married', 'Married')], string='Marital Status', default="single")
    is_corpo_tieup = fields.Boolean(string='Corporate Tie-Up', 
        help="If not checked, these Corporate Tie-Up Group will not be visible at all.")
    corpo_company_id = fields.Many2one('res.partner', string='Corporate Company', 
        domain="[('is_company', '=', True),('customer_rank', '>', 0)]", ondelete='restrict')
    emp_code = fields.Char(string='Employee Code')
    user_id = fields.Many2one('res.users', string='Related User', ondelete='cascade', 
        help='User-related data of the patient')
    primary_doctor = fields.Many2one('hms.physician', 'Primary Care Doctor', ondelete='restrict')
    ref_doctor = fields.Many2many('res.partner', 'rel_doc_pat', 'doc_id', 
        'patient_id', 'Referring Doctors', domain=[('is_referring_doctor','=',True)])
    #ACS NOTE: CAN BE deleted?
    hospitalized = fields.Boolean()
    discharged = fields.Boolean()

    #Diseases
    medical_history = fields.Text(string="Past Medical History")
    patient_diseases = fields.One2many('hms.patient.disease', 'patient_id', string='Diseases')

    #Family Form Tab
    genetic_risks = fields.One2many('hms.patient.genetic.risk', 'patient_id', 'Genetic Risks')
    family_history = fields.One2many('hms.patient.family.diseases', 'patient_id', 'Family Diseases History')
    department_ids = fields.Many2many('hr.department', 'patint_department_rel','patient_id', 'department_id',
        domain=[('patient_depatment', '=', True)], string='Departments')

    medications = fields.One2many('hms.patient.medication', 'patient_id', string='Medications')
    ethnic_group = fields.Many2one('acs.ethnicity', string='Ethnic group')
    cod = fields.Many2one('hms.diseases', string='Cause of Death')
    family_member_ids = fields.One2many('acs.family.member', 'patient_id', string='Family')

    invoice_count = fields.Integer(compute='_rec_count', string='# Invoices')
    prescription_count = fields.Integer(compute='_rec_count', string='# Prescriptions')
    treatment_count = fields.Integer(compute='_rec_count', string='# Treatments')
    appointment_count = fields.Integer(compute='_rec_count', string='# Appointments')
    appointment_ids = fields.One2many('hms.appointment', 'patient_id', 'Appointments')
    medical_alert_ids = fields.Many2many('acs.medical.alert', 'patient_medical_alert_rel','patient_id', 'alert_id',
        string='Medical Alerts')
    occupation = fields.Char("Occupation")
    religion = fields.Char("Religion")
    caste = fields.Char("Tribe")
    registration_product_id = fields.Many2one('product.product', default=_get_service_id, string="Registration Service")
    invoice_id = fields.Many2one("account.move","Registration Invoice")

    @api.model
    def create(self, values):
        if values.get('code','/')=='/':
            values['code'] = self.env['ir.sequence'].next_by_code('hms.patient') or ''
        values['customer_rank'] = True
        return super(ACSPatient, self).create(values)

    @api.onchange('state_id')
    def onchange_state(self):
        if self.state_id:
            self.country_id = self.state_id.country_id.id

    def create_invoice(self):
        product_id = self.registration_product_id or self.env.user.company_id.patient_registration_product_id
        if not product_id:
            raise UserError(_("Please Configure Registration Product in Configuration first."))

        invoice = self.acs_create_invoice(patient=self, product_data=[{'product_id': product_id}])
        self.invoice_id = invoice.id

    def view_invoices(self):
        invoices = self.env['account.move'].search([('partner_id','=',self.partner_id.id)])
        action = self.acs_action_view_invoice(invoices)
        action['context'].update({
            'default_partner_id': self.partner_id.id,
            'default_patient_id': self.id,
        })
        return action

    def action_appointment(self):
        action = self.env.ref('acs_hms.action_appointment').read()[0]
        action['domain'] = [('patient_id','=',self.id)]
        action['context'] = {'default_patient_id': self.id, 'default_physician_id': self.primary_doctor.id, 'default_urgency': 'a'}
        return action

    def action_prescription(self):
        action = self.env.ref('acs_hms.act_open_hms_prescription_order_view').read()[0]
        action['domain'] = [('patient_id','=',self.id)]
        action['context'] = {'default_patient_id': self.id, 'default_physician_id': self.primary_doctor.id}
        return action

    def action_treatment(self):
        action = self.env.ref('acs_hms.acs_action_form_hospital_treatment').read()[0]
        action['domain'] = [('patient_id','=',self.id)]
        action['context'] = {'default_patient_id': self.id, 'default_physician_id': self.primary_doctor.id}
        return action

    @api.model
    def send_birthday_email(self):
        wish_template_id = self.env.ref('acs_hms.email_template_birthday_wish', raise_if_not_found=False)
        today = datetime.now()
        today_month_day = '%-' + today.strftime('%m') + '-' + today.strftime('%d')
        patient_ids = self.search([('birthday', 'like', today_month_day)])
        for patient_id in patient_ids:
            if patient_id.email:
                wish_temp = patient_id.company_id.birthday_mail_template or wish_template_id
                wish_temp.sudo().send_mail(patient_id.id, force_send=True)


class ACSFamilyMember(models.Model):
    _name = 'acs.family.member'
    _description= 'Family Member'

    member = fields.Many2one('res.partner', string='Member', help='Family Member Name')
    role = fields.Char(string='Relation', required=True)
    patient_id = fields.Many2one('hms.patient', string='Patient')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: