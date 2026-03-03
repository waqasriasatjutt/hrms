# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


class AppointmentPurpose(models.Model):
    _name = 'appointment.purpose'
    _description = "Appointment Purpose"

    name = fields.Char(string='Appointment Purpose', required=True, translate=True)


class AppointmentCabin(models.Model):
    _name = 'appointment.cabin'
    _description = "Appointment Cabin"

    name = fields.Char(string='Appointment Cabin', required=True, translate=True)


class Appointment(models.Model):
    _name = 'hms.appointment'
    _description = "Appointment"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'acs.hms.mixin']

    @api.model
    def _get_service_id(self):
        consultation = False
        if self.env.user.company_id.consultation_product_id:
            consultation = self.env.user.company_id.consultation_product_id.id
        return consultation

    @api.onchange('department_id')
    def onchange_department(self):
        res = {}
        if self.department_id:
            physicians = self.env['hms.physician'].search([('department_ids', 'in', self.department_id.id)])
            res['domain'] = {'physician_id':[('id','in',physicians.ids)]}
        return res

    @api.depends('medical_alert_ids')
    def _get_alert_count(self):
        for rec in self:
            rec.alert_count = len(rec.medical_alert_ids)

    @api.depends('patient_id', 'patient_id.birthday', 'date')
    def get_patient_age(self):
        for rec in self:
            age = ''
            if rec.patient_id.birthday:
                end_data = rec.date or fields.Datetime.now()
                delta = relativedelta(end_data, rec.patient_id.birthday)
                if delta.years <= 2:
                    age = str(delta.years) + _(" Year") + str(delta.months) + _(" Month ") + str(delta.days) + _(" Days")
                else:
                    age = str(delta.years) + _(" Year")
            rec.age = age

    READONLY_STATES = {'cancel': [('readonly', True)], 'done': [('readonly', True)]}

    name = fields.Char(string='Appointment Id', readonly=True, copy=False, states=READONLY_STATES)
    patient_id = fields.Many2one('hms.patient', ondelete='restrict',  string='Patient',
        required=True, index=True,help='Patient Name', states=READONLY_STATES, track_visibility='onchange')
    age = fields.Char(compute="get_patient_age", string='Age', store=True,
                      help="Computed patient age at the moment of the evaluation", readonly=False)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string='Gender', default='male', readonly=False)
    phone = fields.Char(String='Phone')
    cnic = fields.Char(String='CNIC')
    fee = fields.Integer(String="Fees")
    image_128 = fields.Binary(related='patient_id.image_128',string='Image', readonly=True)
    physician_id = fields.Many2one('hms.physician', ondelete='restrict', string='Physician', 
        index=True, help='Physician\'s Name', states=READONLY_STATES, track_visibility='onchange')
    department_id = fields.Many2one('hr.department', ondelete='restrict', 
        domain=[('patient_depatment', '=', True)], string='Department', states=READONLY_STATES)
    no_invoice = fields.Boolean(string='Invoice Exempt', states=READONLY_STATES)
    date = fields.Datetime(string='Date', default=fields.Datetime.now, states=READONLY_STATES)
    
    follow_date = fields.Datetime(string="Follow Up Date", states=READONLY_STATES)
    weight = fields.Float(string='Weight', states=READONLY_STATES)
    temp = fields.Char(string='Temp', states=READONLY_STATES)
    hr = fields.Char(string='HR', help="Heart Rate", states=READONLY_STATES)
    rr = fields.Char(string='RR', states=READONLY_STATES, help='Respiratory Rate')
    bp = fields.Char(string='BP', states=READONLY_STATES, help='Blood Pressure')
    spo2 = fields.Char(string='SpO2', states=READONLY_STATES, 
        help='Oxygen Saturation, percentage of oxygen bound to hemoglobin')
    differencial_diagnosis = fields.Text(string='Differencial Diagnosis', states=READONLY_STATES)
    medical_advice = fields.Text(string='Medical Advice', states=READONLY_STATES)
    chief_complain = fields.Text(string='Chief Complaints', states=READONLY_STATES)
    present_illness = fields.Text(string='History of Present Illness', states=READONLY_STATES)
    lab_report = fields.Text(string='Lab Report', states=READONLY_STATES)
    radiological_report = fields.Text(string='Radiological Report', states=READONLY_STATES)
    notes = fields.Text(string='Notes', states=READONLY_STATES)
    past_history = fields.Text(string='Past History', states=READONLY_STATES)
    invoice_id = fields.Many2one('account.move', string='Invoice', ondelete='cascade', track_visibility='onchange')
    urgency = fields.Selection([
            ('a', 'Normal'),
            ('b', 'Urgent'),
            ('c', 'Medical Emergency'),
        ], string='Urgency Level', default='a', 
        states=READONLY_STATES)
    state = fields.Selection([
            ('draft', 'Draft'),
            ('confirm', 'Confirm'),
            ('waiting', 'Waiting'),
            ('in_consultation', 'In consultation'),
            ('pause', 'Pause'),
            ('to_invoice', 'To Invoice'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
        ], string='State',default='draft', required=True, copy=False, 
        states=READONLY_STATES)
    product_id = fields.Many2one('product.product', ondelete='restrict', 
        string='Consultation Service', help="Consultation Services", 
        domain=[('hospital_product_type', '=', "consultation")], required=True, 
        default=_get_service_id, states=READONLY_STATES)
    company_id = fields.Many2one('res.company', ondelete='restrict', states=READONLY_STATES,
        string='Hospital', default=lambda self: self.env.user.company_id.id)
    anytime_invoice = fields.Boolean(related="company_id.appointment_anytime_invoice")
    advance_invoice = fields.Boolean(related="company_id.appo_invoice_advance")
    no_invoice = fields.Boolean('Invoice Exempt', states=READONLY_STATES)
    consultation_type = fields.Selection([
        ('consultation','Consultation'),
        ('followup','Follow Up')],'Consultation Type', states=READONLY_STATES)

    #Diseases
    diseas_id = fields.Many2one('hms.diseases', 'Disease', states=READONLY_STATES)
    medical_history = fields.Text(related='patient_id.medical_history', 
        string="Past Medical History", readonly=True)
    patient_diseases = fields.One2many('hms.patient.disease', 
        related='patient_id.patient_diseases', string='Diseases', 
        help='Mark if the patient has died', readonly=True)

    duration = fields.Float(string='Duration', default=15.00, states=READONLY_STATES)
    waiting_date_start = fields.Datetime('Waiting Start Date', states=READONLY_STATES)
    waiting_date_end = fields.Datetime('Waiting end Date', states=READONLY_STATES)
    waiting_duration = fields.Float('Wait Time', readonly=True)
    waiting_duration_timer = fields.Float('Wait Timer', readonly=True, default="0.1")

    waiting_duration = fields.Float('Wait Time', readonly=True)
    waiting_duration_timer = fields.Float('Wait Timer', readonly=True, default="0.1")

    date_start = fields.Datetime(string='Start Date', states=READONLY_STATES)
    date_end = fields.Datetime(string='End Date', states=READONLY_STATES)
    appointment_duration = fields.Float('Consultation Time', readonly=True)
    appointment_duration_timer = fields.Float('Consultation Timer', readonly=True, default="0.1")

    purpose_id = fields.Many2one('appointment.purpose', ondelete='cascade', 
        string='Purpose', help="Appointment Purpose", states=READONLY_STATES)
    cabin_id = fields.Many2one('appointment.cabin', ondelete='cascade', 
        string='Cabin', help="Appointment Cabin", states=READONLY_STATES)
    treatment_id = fields.Many2one('hms.treatment', ondelete='cascade', 
        string='Treatment', help="Treatment Id", states=READONLY_STATES)

    ref_physician_id = fields.Many2one('res.partner', ondelete='restrict', string='Referring Physician', 
        index=True, help='Referring Physician', states=READONLY_STATES)
    responsible_id = fields.Many2one('hms.physician', "Responsible Nurse/Doctor", states=READONLY_STATES)
    medical_alert_ids = fields.Many2many('acs.medical.alert', 'appointment_medical_alert_rel','appointment_id', 'alert_id',
        string='Medical Alerts', related='patient_id.medical_alert_ids')
    alert_count = fields.Integer(compute='_get_alert_count', default=0)
    consumable_line_ids = fields.One2many('hms.consumable.line', 'appointment_id',
        string='Consumable Line', states=READONLY_STATES)
    #Only used in case of advance invoice
    consumable_invoice_id = fields.Many2one('account.move', string="Consumables Invoice", ondelete='cascade', track_visibility='onchange')

    pause_date_start = fields.Datetime('Pause Start Date', states=READONLY_STATES)
    pause_date_end = fields.Datetime('Pause end Date', states=READONLY_STATES)
    pause_duration = fields.Float('Paused Time', readonly=True)
    prescription_ids = fields.One2many('prescription.order', 'appointment_id', 'Prescriptions')

    @api.model
    def create(self, values):
        if values.get('name', 'New Appointment') == 'New Appointment':
            values['name'] = self.env['ir.sequence'].next_by_code('hms.appointment') or 'New Appointment'
        return super(Appointment, self).create(values)

    def unlink(self):
        for data in self:
            if data.state in ['done']:
                raise UserError(_('You can not delete record in done state'))
        return super(Appointment, self).unlink()

    def print_report(self):
        return self.env.ref('acs_hms.action_appointment_report').report_action(self)

    def action_appointment_send(self):
        '''
        This function opens a window to compose an email, with the template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('acs_hms', 'acs_appointment_email')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'hms.appointment',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def create_invoice(self):
        product_id = self.product_id
        if not product_id:
            raise UserError(_("Please Set Consultation Service first."))
        product_data = [{'product_id': product_id}]
        for consumable in self.consumable_line_ids:
            product_data.append({
                'product_id': consumable.product_id,
                'quantity': consumable.qty,
            })
        inv_data = {
            'ref_physician_id': self.ref_physician_id and self.ref_physician_id.id or False,
            'physician_id': self.physician_id and self.physician_id.id or False,
        }
        invoice = self.acs_create_invoice(patient=self.patient_id, product_data=product_data, inv_data=inv_data)
        self.invoice_id = invoice.id
        if self.state == 'to_invoice':
            self.state = 'done'
        if self.state == 'draft':
            self.appointment_confirm()

    def create_consumed_prod_invoice(self):
        product_data = []
        if not self.consumable_line_ids:
            raise UserError(_("There is no consumed product to invoice."))

        for consumable in self.consumable_line_ids:
            product_data.append({
                'product_id': consumable.product_id,
                'quantity': consumable.qty,
            })
        inv_data = {
            'ref_physician_id': self.ref_physician_id and self.ref_physician_id.id or False,
            'physician_id': self.physician_id and self.physician_id.id or False,
        }
        invoice = self.acs_create_invoice(patient=self.patient_id, product_data=product_data, inv_data=inv_data)
        self.consumable_invoice_id = invoice.id
        if self.state == 'to_invoice':
            self.state = 'done'

    def view_invoice(self):
        invoices = self.mapped('invoice_id') + self.mapped('consumable_invoice_id')
        action = self.acs_action_view_invoice(invoices)
        action['context'].update({
            'default_partner_id': self.patient_id.partner_id.id,
            'default_patient_id': self.patient_id.id,
        })
        return action

    def action_refer_doctor(self):
        action = self.env.ref('acs_hms.action_appointment').read()[0]
        action['domain'] = [('patient_id','=',self.id)]
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_physician_id': self.physician_id.id, 'default_urgency': 'a'}
        action['views'] = [(self.env.ref('acs_hms.view_hms_appointment_form').id, 'form')]
        return action

    @api.onchange('patient_id')
    def onchange_patient_id(self):
        if self.patient_id:
            self.age = self.patient_id.age
            self.phone = self.patient_id.phone
            self.cnic = self.patient_id.cnic
            self.gender = self.patient_id.gender
            followup_days = self.env.user.company_id.followup_days
            followup_day_limit = (datetime.now() + timedelta(days=followup_days)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            appointment_id = self.search([('patient_id', '=', self.patient_id.id),('date','<=',followup_day_limit)])
            self.physician_id = self.patient_id.primary_doctor and self.patient_id.primary_doctor.id
            if appointment_id:
                self.consultation_type = 'followup'
                if self.env.user.company_id.followup_product_id:
                    self.product_id = self.env.user.company_id.followup_product_id.id
            else:
                self.consultation_type = 'consultation'

    @api.onchange('physician_id')
    def onchange_physician(self):
        if self.physician_id:
            self.product_id = self.physician_id.consul_service.id or False
            if self.consultation_type=='followup':
                if self.physician_id.followup_service:
                    self.product_id = self.physician_id.followup_service.id

                elif self.env.user.company_id.followup_product_id:
                   self.product_id = self.env.user.company_id.followup_product_id.id

    def appointment_confirm(self):
        if self.company_id.appo_invoice_advance and not self.invoice_id:
            raise UserError(_('Invoice is not created yet'))
        self.state = 'confirm'

    def appointment_waiting(self):
        self.state = 'waiting'
        self.waiting_date_start = datetime.now()
        self.waiting_duration = 0.1

    def appointment_consultation(self):
        if not self.waiting_date_start:
            raise UserError(('No waiting start time defined.'))
        datetime_diff = datetime.now() - self.waiting_date_start
        m, s = divmod(datetime_diff.total_seconds(), 60)
        h, m = divmod(m, 60)
        self.waiting_duration = float(('%0*d')%(2,h) + '.' + ('%0*d')%(2,m*1.677966102))
        self.state = 'in_consultation'
        self.waiting_date_end = datetime.now()
        self.date_start = datetime.now()

    def action_pause(self):
        self.state = 'pause'
        self.pause_date_start = datetime.now()

        if self.date_start:
            datetime_diff = datetime.now() - self.date_start
            m, s = divmod(datetime_diff.total_seconds(), 60)
            h, m = divmod(m, 60)
            self.appointment_duration = float(('%0*d')%(2,h) + '.' + ('%0*d')%(2,m*1.677966102)) - self.pause_duration
        self.date_end = datetime.now()

    def action_start_paused(self):
        self.state = 'in_consultation'
        self.pause_date_end = datetime.now()
        self.date_end = False
        datetime_diff = datetime.now() - self.pause_date_start
        m, s = divmod(datetime_diff.total_seconds(), 60)
        h, m = divmod(m, 60)
        self.pause_duration += float(('%0*d')%(2,h) + '.' + ('%0*d')%(2,m*1.677966102))

    def consultation_done(self):
        if self.date_start:
            datetime_diff = datetime.now() - self.date_start
            m, s = divmod(datetime_diff.total_seconds(), 60)
            h, m = divmod(m, 60)
            self.appointment_duration = float(('%0*d')%(2,h) + '.' + ('%0*d')%(2,m*1.677966102)) - self.pause_duration
        self.date_end = datetime.now()
        if (self.no_invoice or self.invoice_id) and not (self.consumable_line_ids and self.advance_invoice and not self.no_invoice and not self.consumable_invoice_id):
            self.state = 'done'
        else:
            self.state ='to_invoice'
        if self.consumable_line_ids:
            self.consume_appointment_material() 

    def appointment_done(self):
        if self.consumable_line_ids and self.advance_invoice and not self.no_invoice and not self.consumable_invoice_id:
            raise UserError(_('Please Create invoice for consumables First.'))
        self.state = 'done'

    def appointment_cancel(self):
        self.state = 'cancel'
        self.waiting_date_start = False
        self.waiting_date_end = False

    def appointment_draft(self):
        self.state = 'draft'

    def action_prescription(self):
        action = self.env.ref('acs_hms.act_open_hms_prescription_order_view').read()[0]
        action['domain'] = [('appointment_id', '=', self.id)]
        action['context'] = {
                'default_patient_id': self.patient_id.id,
                'default_physician_id':self.physician_id.id,
                'default_diseases': self.diseas_id and self.diseas_id.id or False,
                'default_treatment_id': self.treatment_id and self.treatment_id.id or False,
                'default_appointment_id': self.id}
        return action

    def button_pres_req(self):
        action = self.env.ref('acs_hms.act_open_hms_prescription_order_view').read()[0]
        action['domain'] = [('appointment_id', '=', self.id)]
        action['views'] = [(self.env.ref('acs_hms.view_hms_prescription_order_form').id, 'form')]
        action['context'] = {
                'default_patient_id': self.patient_id.id,
                'default_physician_id':self.physician_id.id,
                'default_diseases': self.diseas_id and self.diseas_id.id or False,
                'default_treatment_id': self.treatment_id and self.treatment_id.id or False,
                'default_appointment_id': self.id}
        return action
                
    def consume_appointment_material(self):
        for rec in self:
            if not rec.company_id.appointment_usage_location:
                raise UserError(_('Please define a appointment location where the consumables will be used.'))
            if not rec.company_id.appointment_stock_location:
                raise UserError(_('Please define a appointment location from where the consumables will be taken.'))

            dest_location_id  = rec.company_id.appointment_usage_location.id
            source_location_id  = rec.company_id.appointment_stock_location.id
            for line in rec.consumable_line_ids.filtered(lambda s: not s.move_id):
                move = self.consume_material(source_location_id, dest_location_id,
                    {
                        'product': line.product_id,
                        'qty': line.qty,
                    })
                move.appointment_id = rec.id
                line.move_id = move.id


class ACSAppointmentConsumable(models.Model):
    _name = "hms.consumable.line"
    _description = "List of Consumables"

    name = fields.Char(string='Name',default=lambda self: self.product_id.name)
    product_id = fields.Many2one('product.product', ondelete="cascade", string='Consumable')
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', help='Amount of medication (eg, 250 mg) per dose')
    qty = fields.Float(string='Quantity', default=1.0)
    appointment_id = fields.Many2one('hms.appointment', ondelete="restrict", string='Appointment')
    move_id = fields.Many2one('stock.move', string='Stock Move')
    date = fields.Date("Consumed Date", default=fields.Date.context_today)

    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.product_uom = self.product_id.uom_id.id


class StockMove(models.Model):
    _inherit = "stock.move"

    appointment_id = fields.Many2one('hms.appointment', string="Appointment", ondelete="restrict")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: