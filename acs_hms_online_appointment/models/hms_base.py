# -*- encoding: utf-8 -*-
from odoo import api, fields, models,_
from datetime import datetime
from datetime import timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT,DEFAULT_SERVER_DATE_FORMAT


class Appointment(models.Model):
    _inherit = 'hms.appointment'

    @api.depends('date')
    def _get_schedule_date(self):
        for rec in self:
            rec.schedule_date = rec.date.date()

    schedule_date = fields.Date(string='Schedule Date', compute="_get_schedule_date", store=True)
    schedule_slot_id = fields.Many2one('appointment.schedule.slot.lines', string = 'Schedule Slot')
    booked_online = fields.Boolean('Booked Online')

    @api.model
    def clear_appointment_cron(self):
        if self.env.user.company_id.allowed_booking_payment:
            appointments = self.search([('booked_online','=', True),('invoice_id.state','!=','paid'),('state','=','draft')])
            for appointment in appointments:
                #cancel appointment after 20 minute if not paid
                create_time = appointment.create_date + timedelta(minutes=20)
                if create_time <= datetime.now():
                    appointment.invoice_id.action_invoice_cancel()
                    appointment.state = 'cancel'


class HrDepartment(models.Model):
    _inherit = "hr.department"

    allowed_online_booking = fields.Boolean("Allowed Online Booking", default=False)


class HmsPhysician(models.Model):
    _inherit = "hms.physician"

    allowed_online_booking = fields.Boolean("Allowed Online Booking", default=False)
