# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Physiotherapy(models.Model):
    _inherit = 'acs.physiotherapy'

    subscription_id = fields.Many2one("acs.hms.subscription", "Subscription", ondelete="restrict")

    @api.onchange("subscription_id")
    def onchange_subscription_id(self):
        if self.subscription_id:
            self.no_invoice = True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: