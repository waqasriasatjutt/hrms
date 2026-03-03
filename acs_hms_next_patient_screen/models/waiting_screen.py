# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AcsHmsWaitingScreen(models.Model):
    _name = 'acs.hms.waiting.screen'
    _description = "Waiting Screen"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'website.published.multi.mixin']

    name = fields.Char(string='Screen Name', required=True)
    code = fields.Char(string='Code')
    physician_ids = fields.Many2many('hms.physician', 'hms_physician_waiting_screen_rel','physician_id', 'screen_id', string='Physicians')

    def _compute_website_url(self):
        super(AcsHmsWaitingScreen, self)._compute_website_url()
        for record in self:
            record.website_url = "/waiting_screen/%s" % (record.id,)