# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class Appointment(models.Model):
    _inherit = 'hms.appointment'

    READONLY_STATES = {'cancel': [('readonly', True)], 'done': [('readonly', True)]}

    lmp = fields.Date(string='LMP', help="Last Menstrual Period", states=READONLY_STATES)
    induction = fields.Char(string='Induction', states=READONLY_STATES)
    induction_remarks = fields.Char(string='Induction Remarks', states=READONLY_STATES)
    hsg = fields.Char(string='HSG', states=READONLY_STATES)
    hsg_remarks = fields.Char(string='HSG Remarks', states=READONLY_STATES)
    follicular_study = fields.Char(string='Follicular Study', states=READONLY_STATES)
    follicular_study_remarks = fields.Char(string='Follicular Study Remarks', states=READONLY_STATES)
    dhl = fields.Char(string='DHL', help="Diagnostic Hystero Laparoscopy", states=READONLY_STATES)
    dhl_remarks = fields.Char(string='DHL Remarks', states=READONLY_STATES)
    iui = fields.Char(string='IUI', help="Intrauterine Insemination", states=READONLY_STATES)
    iui_remarks = fields.Char(string='IUI Remarks', states=READONLY_STATES)
    ivf = fields.Char(string='IVF', help="In Vitro Fertilization", states=READONLY_STATES)
    ivf_remarks = fields.Char(string='IVF Remarks', states=READONLY_STATES)
    examination_ids = fields.One2many('systemic.examination', 'appointment_id',string='Examinations', states=READONLY_STATES)

    rs = fields.Text(string='R.S.', states=READONLY_STATES)
    cvs = fields.Text(string='CVS.', states=READONLY_STATES, 
        help="Describe about Chorionic villus sampling. : biopsy of a villus of the chorion at usually 10 to 12 weeks of gestation to obtain fetal cells for the prenatal diagnosis of chromosomal abnormalities.")
    cns = fields.Text(string='CNS', states=READONLY_STATES, 
        help="Describe about Central Nerve System malformations. Neural tube defects are the most frequent CNS malformations")
    external_genitals = fields.Text(string='External Genitals', states=READONLY_STATES, help="External Genesis of fetus")
    back_spine = fields.Text(string='Back Spine', states=READONLY_STATES, help="Describe about Back Spine of fetus")
    peripheral_pulsation = fields.Text(string='Peripheral Pulsation', states=READONLY_STATES, help="Measuring Pulse pressure")

    sonography_obstetric_ids = fields.One2many('hms.appointment.sonography.obstetric', 'appointment_id',string='Sonography Obstetric Reports')
    sonography_pelvis_ids = fields.One2many('hms.appointment.sonography.pelvis', 'appointment_id',string='Sonography Pelvis Reports')
    sonography_follical_ids = fields.One2many('hms.appointment.sonography.follical', 'appointment_id',string='Sonography Follical Reports')

    gender = fields.Selection([
        ('male', 'Male'), 
        ('female', 'Female'), 
        ('other', 'Other')], related="patient_id.gender", string='Gender', readonly=True)


class ACSPatient (models.Model):
    _inherit = "hms.patient"

    def _rec_count(self):
        rec = super(ACSPatient, self)._rec_count()
        for rec in self:
            rec.child_birth_count = len(rec.child_birth_ids)

    child_birth_ids = fields.One2many('acs.child.birth', 'patient_id',string='Child Birth')
    child_birth_count = fields.Integer(compute='_rec_count', string='# Child Birth')
    sonography_obstetric_ids = fields.One2many('hms.appointment.sonography.obstetric', 'patient_id',string='Sonography Obstetric Reports')
    sonography_pelvis_ids = fields.One2many('hms.appointment.sonography.pelvis', 'patient_id',string='Sonography Pelvis Reports')
    sonography_follical_ids = fields.One2many('hms.appointment.sonography.follical', 'patient_id',string='Sonography Follical Reports')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: