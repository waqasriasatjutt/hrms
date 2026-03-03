# -*- encoding: utf-8 -*-
from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError
from odoo.tools import pycompat


class CertificateManagement(models.Model):
    _inherit = 'certificate.management'

    patient_id = fields.Many2one('hms.patient', string='Patient', ondelete="restrict", 
        help="Patient whose certificate to be attached", 
        states={'done': [('readonly', True)]})
    physician_id = fields.Many2one('hms.physician',string='Doctor', ondelete="restrict", 
        help="Doctor who provided certificate to the patient", 
        states={'done': [('readonly', True)]})

    @api.onchange('patient_id')
    def onchange_patient_id(self):
        if self.patient_id:
            self.partner_id = self.patient_id.partner_id

    @api.onchange('physician_id')
    def onchange_physician_id(self):
        if self.physician_id:
            self.user_id = self.physician_id.user_id


class ACSPatient(models.Model):
    _inherit = 'hms.patient' 

    def _rec_count(self):
        rec = super(ACSPatient, self)._rec_count()
        for rec in self:
            rec.certificate_count = len(rec.sudo().certificate_ids)

    certificate_ids = fields.One2many('certificate.management', 'patient_id', string='Certificates')
    certificate_count = fields.Integer(compute='_rec_count', string='# Certificates')

    def action_open_certificate(self):
        action = self.env.ref('acs_certification.action_certificate_management').read()[0]
        action['domain'] = [('patient_id','=',self.id)]
        action['context'] = {'default_patient_id': self.id}
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: