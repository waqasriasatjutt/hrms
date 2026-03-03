# -*- coding: utf-8 -*-

import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from odoo.osv import expression


class LabTest(models.Model):
    _name = "acs.lab.test"
    _description = "Lab Test Type"

    name = fields.Char(string='Name', help="Test type, eg X-Ray, hemogram,biopsy...", index=True)
    code = fields.Char(string='Code', help="Short name - code for the test")
    description = fields.Text(string='Description')
    product_id = fields.Many2one('product.product',string='Service', required=True)
    critearea_ids = fields.One2many('lab.test.critearea','test_id', string='Test Cases')
    remark = fields.Char(string='Remark')
    report = fields.Text (string='Test Report')
    company_id = fields.Many2one('res.company', ondelete='restrict', 
        string='Company' ,default=lambda self: self.env.user.company_id.id)

    _sql_constraints = [('code_uniq', 'unique (name)', 'The Lab Test code must be unique')]

    def name_get(self):
        res = []
        for rec in self:
            name = rec.name
            if rec.code:
                name = "%s [%s]" % (rec.name, rec.code)
            res += [(rec.id, name)]
        return res

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []

        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            connector = '&' if operator in expression.NEGATIVE_TERM_OPERATORS else '|'
            domain = [connector, ('code', operator, name), ('name', operator, name)]
        records = self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        return self.browse(records).name_get()


class PatientLabTest(models.Model):
    _name = "patient.laboratory.test"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Patient Laboratory Test"
    _order = 'date_analysis desc, id desc'

    STATES = {'cancel': [('readonly', True)], 'done': [('readonly', True)]}

    def _acs_attachemnt_count(self):
        AttachmentObj = self.env['ir.attachment']
        for rec in self:
            attachments = AttachmentObj.search([
                ('res_model', '=', self._name),
                ('res_id', '=', rec.id)])
            rec.attachment_ids = [(6,0,attachments.ids)]
            rec.attach_count = len(attachments.ids)

    attach_count = fields.Integer(compute="_acs_attachemnt_count", readonly=True, string="Documents")
    attachment_ids = fields.Many2many('ir.attachment', 'attachment_laboratory_rel', 'laboratory_id', 'attachment_id', compute="_acs_attachemnt_count", string="Attachments")

    name = fields.Char(string='Test ID', help="Lab result ID", readonly="1",copy=False, index=True)
    test_id = fields.Many2one('acs.lab.test', string='Test', required=True, ondelete='restrict', states=STATES)
    patient_id = fields.Many2one('hms.patient', string='Patient', required=True, ondelete='restrict', states=STATES)
    age = fields.Integer(string='Age')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')],
        string='Gender', default='male')
    phone = fields.Char(string='Phone')
    cnic = fields.Char(string="CINIC")
    pathologist_id = fields.Many2one('res.users', string='Pathologist', help="Pathologist", ondelete='restrict', states=STATES)
    user_id = fields.Many2one('res.users',string='Pathologist User', default=lambda self: self.env.user, states=STATES)
    physician_id = fields.Many2one('hms.physician',string='Prescribing Doctor', help="Doctor who requested the test", ondelete='restrict', states=STATES)
    diagnosis = fields.Text(string='Diagnosis', states=STATES)
    critearea_ids = fields.One2many('lab.test.critearea', 'patient_lab_id', string='Test Cases', copy=True, states=STATES)
    date_requested = fields.Datetime(string='Request Date', states=STATES)
    date_analysis = fields.Date(string='Test Date', default=fields.Date.context_today, states=STATES)
    request_id = fields.Many2one('acs.laboratory.request', string='Lab Request', ondelete='restrict', states=STATES)
    report = fields.Text(string='Test Report', states=STATES)
    note = fields.Text(string='Extra Info', states=STATES)
    hospitalization_id = fields.Many2one('acs.hospitalization', string='Hospitalization', ondelete='restrict', states=STATES)
    print_in_discharge = fields.Boolean("Print in Discharge Report")
    appointment_id = fields.Many2one('hms.appointment', string='Appointment', ondelete='restrict', states=STATES)
    treatment_id = fields.Many2one('hms.treatment', string='Treatment', ondelete='restrict', states=STATES)
    company_id = fields.Many2one('res.company', ondelete='restrict', 
        string='Company',default=lambda self: self.env.user.company_id.id, states=STATES)
    state = fields.Selection([
        ('draft','Draft'),
        ('done','Done'),
        ('cancel','Cancel'),
    ], string='State',readonly=True, default='draft')

    _sql_constraints = [('id_uniq', 'unique (name)', 'The test ID code must be unique')]

    def action_view_attachments(self):
        self.ensure_one()
        action = self.env.ref('base.action_attachment').read()[0]
        action['domain'] = [('id', 'in', self.attachment_ids.ids)]
        action['context'] = {
                'default_res_model': self._name,
                'default_res_id': self.id,
                'default_is_document': True}
        return action

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('patient.laboratory.test')
        return super(PatientLabTest, self).create(vals)

    def unlink(self):
        for rec in self:
            if rec.state not in ['draft']:
                raise UserError(_("Lab Test can be delete only in Draft state."))
        return super(PatientLabTest, self).unlink()

    @api.onchange('request_id')
    def onchange_request_id(self):
        if self.request_id and self.request_id.date:
            self.requested_date = self.request_id.date

    @api.onchange('test_id')
    def on_change_test(self):
        test_lines = [] 
        if self.test_id:
            self.results = self.test_id.description
            for line in self.test_id.critearea_ids:
                test_lines.append((0,0,{
                    'sequence': line.sequence,
                    'name': line.name,
                    'normal_range': line.normal_range,
                    #'result': line.result,
                    'uom_id': line.uom_id and line.uom_id.id or False,
                    'remark': line.remark,
                }))
            self.critearea = test_lines

    def action_done(self):
        self.state = 'done'

    def action_cancel(self):
        self.state = 'cancel'


class LabTestCritearea(models.Model):
    _name = "lab.test.critearea"
    _description = "Lab Test Critearea"
    _order="sequence"

    name = fields.Char('Parameter')
    sequence = fields.Integer('Sequence',default=100)
    result = fields.Char('Result')
    uom_id = fields.Many2one('uom.uom', string='UOM')
    remark = fields.Char('Remark')
    normal_range = fields.Char('Normal Range')
    test_id = fields.Many2one('acs.lab.test','Test type', ondelete='cascade')
    patient_lab_id = fields.Many2one('patient.laboratory.test','Lab Test', ondelete='cascade')
    request_id = fields.Many2one('acs.laboratory.request', 'Lab Request', ondelete='cascade')
    company_id = fields.Many2one('res.company', ondelete='restrict', 
        string='Company',default=lambda self: self.env.user.company_id.id)
    display_type = fields.Selection([
        ('line_section', "Section")], default=False, help="Technical field for UX purpose.")


class PatientLabTestLine(models.Model):
    _name = "laboratory.request.line"
    _description = "Test Lines"

    test_id = fields.Many2one('acs.lab.test',string='Test', ondelete='cascade', required=True)
    instruction = fields.Char(string='Special Instructions')
    request_id = fields.Many2one('acs.laboratory.request',string='Lines', ondelete='restrict')
    sale_price = fields.Float(string='Sale Price')
    company_id = fields.Many2one('res.company', ondelete='restrict', 
        string='Company',related='request_id.company_id') 

    @api.onchange('test_id')
    def onchange_test(self):
        if self.test_id:
            self.sale_price = self.test_id.product_id.lst_price


class LaboratoryRequest(models.Model):
    _name = 'acs.laboratory.request'
    _description = 'Laboratory Request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'acs.hms.mixin']
    
    @api.depends('line_ids')
    def _get_total_price(self):
        self.total_price = sum(line.sale_price for line in self.line_ids)

    STATES = {'requested': [('readonly', True)], 'accepted': [('readonly', True)], 'in_progress': [('readonly', True)], 'cancel': [('readonly', True)], 'done': [('readonly', True)]}

    name = fields.Char(string='Lab Request ID', readonly=True, index=True, copy=False)
    appointment_id = fields.Many2one('hms.appointment', string='Appointment', ondelete='restrict', states=STATES)
    hospitalization_id = fields.Many2one('acs.hospitalization', string='Hospitalization', ondelete='restrict', states=STATES)
    treatment_id = fields.Many2one('hms.treatment', string='Treatment', ondelete='restrict', states=STATES)
    notes = fields.Text(string='Notes', states=STATES)
    date = fields.Datetime('Date', readonly=True, default=fields.Datetime.now, states=STATES)
    state = fields.Selection([
        ('draft','Draft'),
        ('requested','Requested'),
        ('accepted','Accepted'),
        ('in_progress','In Progress'),
        ('cancel','Cancel'),
        ('done','Done')],
        string='State',readonly=True, default='draft')
    patient_id = fields.Many2one('hms.patient', string='Patient', required=True, ondelete='restrict', states=STATES)
    age = fields.Integer(string='Age')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')],
        string='Gender', default='male')
    phone = fields.Char(string='Phone')
    cnic = fields.Char(string="CINIC")

    physician_id = fields.Many2one('hms.physician',
        string='Prescribing Doctor', help="Doctor who Request the lab test.", ondelete='restrict', states=STATES)
    invoice_id = fields.Many2one('account.move',string='Invoice', copy=False, ondelete='restrict', states=STATES)
    line_ids = fields.One2many('laboratory.request.line', 'request_id',
        string='Lab Test Line', states=STATES)
    no_invoice = fields.Boolean(string='Invoice Exempt', states=STATES)
    total_price = fields.Float(compute=_get_total_price, string='Total')
    info = fields.Text(string='Extra Info', states=STATES)
    critearea_ids = fields.One2many('lab.test.critearea', 'request_id', string='Test Cases', states=STATES)
    company_id = fields.Many2one('res.company', ondelete='restrict', 
        string='Company', default=lambda self: self.env.user.company_id.id, states=STATES)
 
    def unlink(self):
        for rec in self:
            if rec.state not in ['draft']:
                raise UserError(_("Lab Requests can be delete only in Draft state."))
        return super(LaboratoryRequest, self).unlink()

    def button_requested(self):
        self.name = self.env['ir.sequence'].next_by_code('acs.laboratory.request')
        self.date = datetime.now()
        self.state = 'requested'

    def button_accept(self):
        self.state = 'accepted'

    def button_in_progress(self):
        self.state = 'in_progress'
        Critearea = self.env['lab.test.critearea']
        LabTest = self.env['patient.laboratory.test']
        for line in self.line_ids:
            test_result = LabTest.create({
                'patient_id': self.patient_id.id,
                'physician_id': self.physician_id and self.physician_id.id,
                'test_id': line.test_id.id,
                'user_id': self.env.user.id,
                'date_analysis': self.date,
                'request_id': self.id,
                'appointment_id': self.appointment_id and self.appointment_id.id,
                'hospitalization_id': self.hospitalization_id and self.hospitalization_id.id,
            })
            for res_line in line.test_id.critearea_ids:
                Critearea.create({
                    'patient_lab_id': test_result.id,
                    'name': res_line.name,
                    'normal_range': res_line.normal_range,
                    'uom_id': res_line.uom_id and res_line.uom_id.id or False,
                    'sequence': res_line.sequence,
                    'remark': res_line.remark,
                    'display_type': res_line.display_type,
                })

    def button_done(self):
        self.state = 'done'

    def button_cancel(self):
        self.state = 'cancel'

    def create_invoice(self):
        if not self.line_ids:
            raise UserError(_("Please add lab Tests first."))

        product_data = []
        for line in self.line_ids:
            product_data.append({
                'product_id': line.test_id.product_id,
            })
        invoice = self.acs_create_invoice(patient=self.patient_id, product_data=product_data, inv_data={})
        self.invoice_id = invoice.id
        invoice.request_id = self.id

    def view_invoice(self):
        invoices = self.mapped('invoice_id')
        action = self.acs_action_view_invoice(invoices)
        return action

    def action_view_test_results(self):
        action = self.env.ref('acs_hms_laboratory.action_lab_result').read()[0]
        action['domain'] = [('request_id','=',self.id)]
        action['context'] = {'default_request_id': self.id, 'default_physician_id': self.physician_id.id}
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: