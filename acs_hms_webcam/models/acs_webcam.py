# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HmsPatient(models.Model):
    _name = 'hms.patient'
    _inherit = ['hms.patient','acs.webcam.mixin']


class HmsPhysician(models.Model):
    _name = 'hms.physician'
    _inherit = ['hms.physician','acs.webcam.mixin']
