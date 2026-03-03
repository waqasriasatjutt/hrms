# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval

class HmsAppointment(models.Model):
    _name = 'hms.appointment'
    _inherit = ['hms.appointment','acs.sms.mixin']


    def appointment_confirm(self):
        res = super(HmsAppointment, self).appointment_confirm()
        if self.env.user.sudo().company_id.appointment_registartion_sms:
            for rec in self:
                if rec.patient_id and rec.patient_id.mobile:
                    msg_exp = self.env.user.sudo().company_id.appointment_registartion_sms
                    msg = eval(msg_exp, {'object': rec})
                    self.create_sms(msg, rec.patient_id.partner_id.mobile, rec.patient_id.partner_id)
        return res

class HmsPatient(models.Model):
    _name = 'hms.patient'
    _inherit = ['hms.patient','acs.sms.mixin']

    @api.model
    def create(self, vals):
        res = super(HmsPatient, self).create(vals)
        if self.env.user.sudo().company_id.patient_registartion_sms:
            if res.mobile:
                msg_exp = self.env.user.sudo().company_id.patient_registartion_sms
                msg = eval(msg_exp, {'object': res})
                self.create_sms(msg, res.partner_id.mobile, res.partner_id)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: