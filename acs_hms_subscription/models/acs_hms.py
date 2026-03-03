# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Appointment(models.Model):
    _inherit = 'hms.appointment'

    subscription_id = fields.Many2one("acs.hms.subscription", "Subscription", ondelete="restrict")

    @api.onchange("subscription_id")
    def onchange_subscription_id(self):
        if self.subscription_id:
            self.no_invoice = True


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    subscription_id = fields.Many2one("acs.hms.subscription", "Subscription", ondelete="restrict")


class ACSPatient (models.Model):
    _inherit = "hms.patient"

    def _do_count(self):
        for rec in self: 
            rec.subscription_count = len(rec.subscription_ids)

    subscription_ids = fields.One2many("acs.hms.subscription", "patient_id", "Subscriptions")
    subscription_count = fields.Integer(string='# of Subscription', compute='_do_count', readonly=True)

    def action_view_subscriptions(self):
        subscriptions = self.subscription_ids
        action = self.env.ref('acs_hms_subscription.acs_hms_subscription_action').read()[0]
        if len(subscriptions) > 1:
            action['domain'] = [('id', 'in', subscriptions.ids)]
        elif len(subscriptions) == 1:
            action['views'] = [(self.env.ref('acs_hms_subscription.acs_hms_subscription_form_view').id, 'form')]
            action['res_id'] = subscriptions.ids[0]
        action.update({'context': {'default_patient_id': self.id}})
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: