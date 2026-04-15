# -*- coding: utf-8 -*-
import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class ZkDevicePunch(models.Model):
    _name = 'zk.device.punch'
    _description = 'ZKTeco Raw Punch'
    _order = 'punch_time desc, id desc'
    _rec_name = 'punch_time'

    device_id = fields.Many2one(
        'zk.device', required=True, ondelete='cascade', index=True,
    )
    pin = fields.Char(
        'PIN', required=True, index=True,
        help='User identifier on the biometric device (matches hr.employee.zk_user_id).',
    )
    punch_time = fields.Datetime(required=True, index=True)
    status = fields.Char(
        help='Raw status code from the device: 0=check_in, 1=check_out, '
             '2=break_out, 3=break_in, 4=overtime_in, 5=overtime_out. '
             'Not currently used for pairing — simple odd/even pairing is applied instead.',
    )
    verify = fields.Char(help='Verification method: 0=password, 1=fingerprint, 2=card, 15=face, etc.')
    workcode = fields.Char()

    employee_id = fields.Many2one('hr.employee', index=True, ondelete='set null')
    attendance_id = fields.Many2one('hr.attendance', ondelete='set null')
    processed = fields.Boolean(default=False, index=True)
    error = fields.Char()

    _sql_constraints = [
        ('uniq_device_pin_time',
         'unique(device_id, pin, punch_time)',
         'Duplicate punch for the same device, user and timestamp.'),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        punches = super().create(vals_list)
        for punch in punches:
            try:
                punch._process_to_attendance()
            except Exception as e:
                punch.error = (str(e) or 'unknown error')[:500]
                _logger.warning("zk.device.punch %s failed to process: %s", punch.id, e)
        return punches

    def _find_employee(self):
        """Resolve the punch's PIN to an hr.employee.

        Match order:
          1. hr.employee.zk_user_id = pin
          2. hr.employee.barcode = pin    (fallback for sites that already use barcode)
        """
        self.ensure_one()
        Employee = self.env['hr.employee'].sudo()
        emp = Employee.search([('zk_user_id', '=', self.pin)], limit=1)
        if not emp:
            emp = Employee.search([('barcode', '=', self.pin)], limit=1)
        return emp

    def _process_to_attendance(self):
        """Pair this punch with the employee's current open attendance,
        or open a new one.

        Simple rule: if there's an open attendance (no check_out) whose
        check_in is *before* this punch, close it. Otherwise create a
        new attendance with check_in = this punch's time.
        """
        self.ensure_one()
        if self.processed:
            return
        emp = self._find_employee()
        if not emp:
            self.write({'error': _('No employee with zk_user_id or barcode = %s') % self.pin})
            return
        Att = self.env['hr.attendance'].sudo()
        # Last open attendance for this employee
        last = Att.search(
            [('employee_id', '=', emp.id)],
            order='check_in desc',
            limit=1,
        )
        if last and not last.check_out and self.punch_time > last.check_in:
            last.check_out = self.punch_time
            self.write({
                'employee_id': emp.id,
                'attendance_id': last.id,
                'processed': True,
                'error': False,
            })
            return
        # Open a new attendance
        new_att = Att.create({
            'employee_id': emp.id,
            'check_in': self.punch_time,
        })
        self.write({
            'employee_id': emp.id,
            'attendance_id': new_att.id,
            'processed': True,
            'error': False,
        })

    def action_reprocess(self):
        for rec in self:
            rec._process_to_attendance()
        return True
