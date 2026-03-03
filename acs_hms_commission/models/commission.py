# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp


class HMSCommission(models.Model):
    _name = 'acs.hms.commission'
    _description = 'HMS Commission'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _invoice_status(self):
        for rec in self:
            if not rec.payment_invoice_id:
                rec.invoice_status = 'not_inv'
            elif rec.payment_invoice_id.state=='draft':
                rec.invoice_status = 'draft'
            elif rec.payment_invoice_id.state=='cancel':
                rec.invoice_status = 'cancel'
            elif rec.payment_invoice_id.invoice_payment_state=='paid':
                rec.invoice_status = 'paid'
            else:
                rec.invoice_status = 'open'

    STATES = {'done': [('readonly', True)], 'cancel': [('readonly', True)]}

    name = fields.Char(string='Name',readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'done'),
        ('cancel', 'Cancelled'),
    ], string='Status', copy=False, default='draft', track_visibility='onchange', states=STATES)
    partner_id = fields.Many2one('res.partner', 'Partner', required=True, states=STATES)
    invoice_id = fields.Many2one('account.move', 'Invoice', states=STATES)
    commission_on = fields.Float('Commission On', states=STATES)
    commission_percentage = fields.Float('Commission Percentage', states=STATES)
    commission_amount = fields.Float('Commission Amount', states=STATES)
    invoice_line_id = fields.Many2one('account.move.line', 'Payment Invoice Line', states=STATES)
    payment_invoice_id = fields.Many2one('account.move', related="invoice_line_id.move_id", string='Payment Invoice', readonly=True)
    invoice_status = fields.Selection([
        ('not_inv', 'Not Invoiced'),
        ('draft', 'Draft Invoice'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('cancel', 'Canceled'), 
    ], string='Invoice Status', copy=False, default='not_inv', readonly=True, compute="_invoice_status")    
    note = fields.Text("Note")

    def unlink(self):
        for rec in self:
            if rec.state not in ('draft', 'cancel'):
                raise UserError(_('You cannot delete an record which is not draft or cancelled.'))
        return super(HMSCommission, self).unlink()

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('acs.hms.commission')
        return super(HMSCommission, self).create(values)

    def action_done(self):
        self.state = 'done'

    def action_draft(self):
        self.state = 'draft'

    def action_cancel(self):
        self.state = 'cancel'