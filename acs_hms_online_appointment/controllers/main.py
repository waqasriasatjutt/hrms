# -*- coding: utf-8 -*-

import babel.dates
import time
import datetime
import pytz
from datetime import timedelta
from dateutil import tz

from odoo import http, fields
from odoo.http import request
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT,DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager


class HMSPortal(CustomerPortal):

    #Appointment Booking
    def create_booking_data(self):
        user = request.env['res.users'].sudo().browse(request.uid)
        values = {
            'error': {},
            'error_message': []
        }

        department_ids = request.env['hr.department'].sudo().search([('allowed_online_booking','=',True)])
        physician_ids = request.env['hms.physician'].sudo().search([('allowed_online_booking','=',True)])
        values.update({
            'slots': [],
            'slot_lines': [],
            'partner': user.partner_id,
            'department_ids': department_ids,
            'physician_ids': physician_ids,
            'appointment_tz': False
        })
        return values

    @http.route(['/create/appointment'], type='http', auth='user', website=True)
    def create_appointment(self, redirect=None, **post):
        values = self.create_booking_data()
        values.update({
            'redirect': redirect,
        })
        return request.render("acs_hms_online_appointment.appointment_details", values)
        
    @http.route(['/save/appointment'], type='http', auth='user', website=True)
    def save_appointment(self, redirect=None, **post):
        env = request.env
        partner = env['res.users'].browse(request.uid).partner_id
        app_obj = env['hms.appointment']
        res_patient = env['hms.patient']
        slot_line = env['appointment.schedule.slot.lines']
        user = env.user.sudo()
        values = {
            'error': {},
            'error_message': [],
            'partner': partner,
        }
        
        patient = res_patient.search([('partner_id', '=', partner.id)],limit=1)
        slot = slot_line.browse(int(post.get('schedule_slot_id')))

        error, error_message = self.validate_application_details(patient, post)
        if error_message:
            values = self.create_booking_data()
            values.update({'error': error, 'error_message': error_message})
            return request.render("acs_hms_online_appointment.appointment_details", values)

        if post:
            now = datetime.datetime.now()
            #user_tz = pytz.timezone(request.context.get('tz') or env.user.tz or 'UTC')
            #app_date = user_tz.localize(slot.from_slot).astimezone(pytz.utc)
            #app_date.replace(tzinfo=None)
            app_date = slot.from_slot

            if app_date < now:
                values.update({'error_message':['Appointment date is past please enter valid.']})
                return request.render("acs_hms_online_appointment.appointment_details", values)

            post.update({
                'schedule_slot_id': slot.id,
                'booked_online':True,
                'patient_id': patient.id,
                'date': app_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            })
            patient.sudo().write({'mobile': post.pop('mobile', '')})
            post.pop('name', '')
            post.pop('slot_date', '')
            # Create Appointment
            app_id = app_obj.sudo().create(post)
            if user.sudo().company_id.allowed_booking_payment:
                app_id.with_context(default_create_stock_moves=False).create_invoice()
                #Instead of validating nvoice just st appointment no to mak it working on portal payment.
                app_id.invoice_id.number = app_id.name
                invoice = app_id.invoice_id
                return request.redirect('/my/invoices/%s#portal_pay' %(invoice.id))

            return request.render("acs_hms_online_appointment.appointment_thank_you", {'appointment': app_id})

        return request.redirect('/my/account')

    def validate_application_details(self, patient, data):
        error = dict()
        error_message = []
        mandatory_fields = ['schedule_slot_id']

        #If no patient 
        if not patient:
            error_message.append(_('No patient is linked with user.'))

        # Mandatory Field Validation
        for field_name in mandatory_fields:
            if not data.get(field_name):
                error[field_name] = 'missing'

        # error message for empty required fields
        if [err for err in error.values() if err == 'missing']:
            error_message.append(_('Some required fields are empty.'))

        return error, error_message

    @http.route(['/acs/get/slotdates'], type='json', auth="public", methods=['POST'], website=True)
    def slot_date_infos(self, **kwargs):
        physician_id = kwargs['args'].get('physician_id')
        department_id = kwargs['args'].get('department_id')
        last_date = fields.Date.today() + timedelta(days=request.env.user.sudo().company_id.allowed_booking_online_days)
        domain = [('slot_date','>=',fields.Date.today()),('slot_date','<=',last_date)]
        if physician_id:
            domain += [('physician_id', '=', int(physician_id))]
        if department_id:
            domain += [('department_id', '=', int(department_id))]
        slots = request.env['appointment.schedule.slot'].sudo().search(domain)
        data = {}
        for slot in slots:
            data[slot.id] = [slot.id,slot.slot_date]
        return data

    @http.route(['/acs/get/slotlines/<model("appointment.schedule.slot"):slot>'], type='json', auth="public", methods=['POST'], website=True)
    def slot_infos(self, slot, **kw):
        slot_lines = request.env['appointment.schedule.slot.lines'].search([('from_slot','>=',fields.Datetime.now()),('slot_id', '=', slot.id),('rem_limit','>=',1)])
        data = {}
        for slot_line in slot_lines:
            data[slot_line.id] = [slot_line.id,slot_line.name]
            data['appointment_tz'] = slot_line.slot_id.appointment_tz
        return data
