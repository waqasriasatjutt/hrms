# -*- coding: utf-8 -*-

from odoo import http, fields, _
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager


class HMSPortal(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super(HMSPortal, self)._prepare_portal_layout_values()
        user = request.env.user
        patient = request.env['hms.patient'].sudo().search([('partner_id', '=', request.env.user.partner_id.id)])
        apps_count = request.env['hms.appointment'].search_count([('patient_id', '=', patient.id)])
        prescription_count = request.env['prescription.order'].search_count([('patient_id', '=', patient.id)])
        values.update({
            'appointment_count': apps_count,
            'prescription_count': prescription_count,
        })
        return values

    @http.route(['/my/appointments', '/my/appointments/page/<int:page>'], type='http', auth="user", website=True)
    def my_appointments(self, page=1, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        user = request.env.user
        if not sortby:
            sortby = 'date'

        sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }

        order = sortings.get(sortby, sortings['date'])['order']
 
        pager = portal_pager(
            url="/my/appointments",
            url_args={},
            total=values['appointment_count'],
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        patient = request.env['hms.patient'].sudo().search([('partner_id.id', '=', request.env.user.partner_id.id)])
        appointments = request.env['hms.appointment'].search([
            ('patient_id.id', '=', patient.id),],
            order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'sortings': sortings,
            'sortby': sortby,
            'appointments': appointments,
            'page_name': 'appointment',
            'default_url': '/my/appointments',
            'searchbar_sortings': sortings,
            'pager': pager
        })
        return request.render("acs_hms_portal.my_appointments", values)

    @http.route(['/my/appointments/<int:appointment_id>'], type='http', auth="user", website=True)
    def my_appointments_appointment(self, appointment_id=None, **kw):
        appointment = request.env['hms.appointment'].browse(appointment_id)
        return request.render("acs_hms_portal.my_appointments_appointment", {'appointment': appointment})

    #Prescriptions
    @http.route(['/my/prescriptions', '/my/prescriptions/page/<int:page>'], type='http', auth="user", website=True)
    def my_prescriptions(self, page=1, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        user = request.env.user
        if not sortby:
            sortby = 'date'

        sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }

        order = sortings.get(sortby, sortings['date'])['order']
 
        pager = portal_pager(
            url="/my/prescriptions",
            url_args={},
            total=values['prescription_count'],
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        patient = request.env['hms.patient'].search([('partner_id', '=', request.env.user.partner_id.id)], limit=1)
        prescriptions = request.env['prescription.order'].search([
            ('patient_id', '=', patient.id)],
            order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'sortings': sortings,
            'sortby': sortby,
            'prescriptions': prescriptions,
            'page_name': 'prescription',
            'default_url': '/my/prescriptions',
            'searchbar_sortings': sortings,
            'pager': pager
        })
        return request.render("acs_hms_portal.my_prescriptions", values)

    @http.route(['/my/prescriptions/<int:prescription_id>'], type='http', auth="user", website=True)
    def my_appointments_prescription(self, prescription_id=None, **kw):
        prescription = request.env['prescription.order'].browse(prescription_id)
        return request.render("acs_hms_portal.my_prescriptions_prescription", {'prescription': prescription})
