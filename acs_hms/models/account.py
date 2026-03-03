# -*- coding: utf-8 -*-

from odoo import api,fields,models,_
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    patient_id = fields.Many2one('hms.patient',  string='Patient', index=True)
    physician_id = fields.Many2one('hms.physician', string='Physician') 
    ref_physician_id = fields.Many2one('res.partner', ondelete='restrict', string='Referring Physician', 
        index=True, help='Referring Physician', readonly=True, states={'draft': [('readonly', False)]})