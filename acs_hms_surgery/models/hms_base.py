# -*- encoding: utf-8 -*-
from odoo import api, fields, models,_


class ACSAppointment(models.Model):
    _inherit = 'hms.appointment'

    surgery_id = fields.Many2one('hms.surgery', ondelete="restrict", string='Surgery',
        invisible=True, states={'cancel': [('readonly', True)], 'done': [('readonly', True)]})


class ACSPatient(models.Model):
    _inherit = "hms.patient"

    def _rec_count(self):
        rec = super(ACSPatient, self)._rec_count()
        for rec in self:
            rec.surgery_count = len(rec.surgery_ids)

    surgery_ids = fields.One2many('hms.surgery', 'patient_id', string='Surgery')
    surgery_count = fields.Integer(compute='_rec_count', string='# Surgery')
    past_surgeries_ids = fields.One2many('past.surgeries', 'patient_id', string='Past Surgerys')

    def action_view_surgery(self):
        action = self.env.ref('acs_hms_surgery.act_open_action_form_surgery').read()[0]
        action['domain'] = [('patient_id', '=', self.id)]
        action['context'] = {'default_patient_id': self.id}
        return action


class ACSConsumableLine(models.Model):
    _inherit = "hms.consumable.line"

    surgery_template_id = fields.Many2one('hms.surgery.template', ondelete="cascade", string='Surgery Template')
    surgery_id = fields.Many2one('hms.surgery', ondelete="cascade", string='Surgery')


class StockMove(models.Model):
    _inherit = "stock.move"

    surgery_id = fields.Many2one('hms.surgery', string='Surgery')
