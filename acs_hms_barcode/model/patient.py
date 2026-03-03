# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

def isodd(x):
    return bool(x % 2)

class ACSPatient(models.Model):
    _inherit = "hms.patient"

    barcode = fields.Char(string='Barcode', help="Number used for Patient identification.")

    _sql_constraints = [('ean13_uniq', 'UNIQUE(barcode)', 'Barcode must be unique!'),]


    def generate_barcode(self):
        ean = self.env['ir.sequence'].next_by_code('patient.barcode') or '/'
        if len(ean) > 12:
            raise UserError(_("There next sequence is upper than 12 characters. This can't work."
                   "You will have to redefine the sequence or create a new one"))
        else:
            ean = (len(ean[0:6]) == 6 and ean[0:6] or ean[0:6].ljust(6,'0')) + ean[6:].rjust(6,'0')
        sum = 0
        for i in range(12):
            if isodd(i):
                sum += 3 * int(ean[i])
            else:
                sum += int(ean[i])
        key = (10 - sum % 10) % 10
        self.barcode = ean + str(key)


class HmsAppointment(models.Model):
    _inherit = 'hms.appointment'

    get_patient_barcode = fields.Char(string='Add Patient', size=13, help="Read a Barcode to set patient detail.")

    @api.onchange('get_patient_barcode')
    def onchange_patient_barcode(self):
        warning = {}
        if self.get_patient_barcode:
            patient_id = self.env['hms.patient'].search([('barcode','=',self.get_patient_barcode)], limit=1)
            if patient_id:
                self.patient_id = patient_id.id
                self.physician_id = patient_id.primary_doctor and patient_id.primary_doctor.id or False
            else:
                warning = {'title': _('Warning!'),
                    'message': _("There is no patient with Barcode: %s") % (self.get_patient_barcode),
                }
            self.get_patient_barcode = False
            return {'warning':warning}


class PrescriptionOder(models.Model):
    _inherit = 'prescription.order'

    get_patient_barcode = fields.Char(string='Add Patient', size=13, help="Read a Barcode to set patient detail.")

    @api.onchange('get_patient_barcode')
    def onchange_patient_barcode(self):
        warning = {}
        if self.get_patient_barcode:
            patient_id = self.env['hms.patient'].search([('barcode','=',self.get_patient_barcode)], limit=1)
            if patient_id:
                self.patient_id = patient_id.id
                self.physician_id = patient_id.primary_doctor and patient_id.primary_doctor.id or False
            else:
                warning = {'title': _('Warning!'),
                    'message': _("There is no patient with Barcode: %s") % (self.get_patient_barcode),
                }
            self.get_patient_barcode = False
            return {'warning':warning}


class HmsTreatment(models.Model):
    _inherit = 'hms.treatment'

    get_patient_barcode = fields.Char(string='Add Patient', size=13, help="Read a Barcode to set patient detail.")

    @api.onchange('get_patient_barcode')
    def onchange_patient_barcode(self):
        warning = {}
        if self.get_patient_barcode:
            patient_id = self.env['hms.patient'].search([('barcode','=',self.get_patient_barcode)], limit=1)
            if patient_id:
                self.patient_id = patient_id.id
                self.physician_id = patient_id.primary_doctor and patient_id.primary_doctor.id or False
            else:
                warning = {'title': _('Warning!'),
                    'message': _("There is no patient with Barcode: %s") % (self.get_patient_barcode),
                }
            self.get_patient_barcode = False
            return {'warning':warning}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    
