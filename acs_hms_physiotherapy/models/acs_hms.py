#-*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ACSAppointment(models.Model):
    _inherit = 'hms.appointment'

    def action_view_physiotherapy(self):
        action = self.env.ref('acs_hms_physiotherapy.acs_action_form_physiotherapy').read()[0]
        action['domain'] = [('appointment_id', '=', self.id)]
        action['context'] = {
            'default_appointment_id': self.id,
            'default_patient_id': self.patient_id.id
        }
        return action

class ACSPatient(models.Model):
    _inherit = "hms.patient"

    def _rec_count(self):
        rec = super(ACSPatient, self)._rec_count()
        for rec in self:
            rec.physiotherapy_count = len(rec.physiotherapy_ids)

    physiotherapy_ids = fields.One2many('acs.physiotherapy', 'patient_id', string='Physiotherapy')
    physiotherapy_count = fields.Integer(compute='_rec_count', string='# Physiotherapy')

    def action_view_physiotherapy(self):
        action = self.env.ref('acs_hms_physiotherapy.acs_action_form_physiotherapy').read()[0]
        action['domain'] = [('patient_id', '=', self.id)]
        action['context'] = {
            'default_patient_id': self.id
        }
        return action
