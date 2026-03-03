# -*- coding: utf-8 -*-
from odoo import api, fields, models

class AcsWebcamMixin(models.AbstractModel):
    _name = "acs.webcam.mixin"
    _description = "ACS Webcam Mixin"

    def _get_acs_webcam_url(self):
        web_base_url = self.env['ir.config_parameter'].sudo().get_param("web.base.url")
        for rec in self:
            rec.acs_webcam_url = web_base_url + '/acs/webcam/' + self._name + '/' + str(rec.id)

    acs_webcam_url = fields.Char(compute='_get_acs_webcam_url')

    @api.model
    def create_sms(self, msg, mobile, partner=False):
        self.env['acs.sms'].create({
            'msg': msg,
            'partner_id': partner and partner.id or False,
            'mobile': mobile,
        })


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner','acs.webcam.mixin']


class ResUsers(models.Model):
    _name = 'res.users'
    _inherit = ['res.users','acs.webcam.mixin']
