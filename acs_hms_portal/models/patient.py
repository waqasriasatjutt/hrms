# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.tools import email_split
from odoo.exceptions import UserError


def extract_email(email):
    """ extract the email address from a user-friendly email address """
    addresses = email_split(email)
    return addresses[0] if addresses else ''


class Patient(models.Model):
    _inherit = 'hms.patient'

    @api.model
    def create(self, values):
        patient = super(Patient, self).create(values)
        if patient.company_id.create_auto_users:
            if not patient.email:
                raise UserError(_('Please define valid email for the Patient'))
            group_portal = self.env.ref('base.group_portal')
            print ("group _poryalllll",group_portal)
            group_portal = group_portal  or False
            user = patient.user_ids[0] if patient.user_ids else None
            # update partner email, if a new one was introduced
            # add portal group to relative user of selected partners
            user_portal = None
            # create a user if necessary, and make sure it is in the portal group
            if not user:
                if patient.company_id:
                    company_id = patient.company_id
                else:
                    company_id = self.env['res.company']._company_default_get('res.users')
                user_portal = patient.sudo().with_context(company_id=company_id)._create_user()
            else:
                user_portal = user
            if group_portal not in user_portal.groups_id:
                user_portal.write({'active': True, 'groups_id': [(4, group_portal.id)]})
                # prepare for the signup process
                patient.partner_id.signup_prepare()
        return patient



    def _create_user(self):
        company_id = self.env.context.get('company_id')
        return self.env['res.users'].with_context(no_reset_password=True).create({
            'email': extract_email(self.email),
            'login': extract_email(self.email),
            'password': extract_email(self.email),
            'partner_id': self.partner_id.id,
            'company_id': company_id.id,
            'company_ids': [(6, 0, [company_id.id])],
            'groups_id': [(6, 0, [])],
        })
