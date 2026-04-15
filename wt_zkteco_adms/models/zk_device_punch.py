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

        Pairing rules (robust against real-device messiness):

        1. Noise filter: if the most recent attendance for this employee has
           either a check_in or check_out within 60 seconds of this punch,
           treat it as a duplicate and skip.
        2. If there is ANY open attendance (no check_out) for this employee,
           close it with this punch — regardless of timestamp ordering.
           This is safe because Odoo forbids two open attendances per employee,
           so there's only ever one "current" session at a time.
        3. Before creating a new attendance, double-check no other attendance
           already covers this exact timestamp (defends against reprocess loops).
        4. Historical backfill: if this punch is older than the employee's
           newest attendance, we intentionally do NOT try to splice it in —
           too ambiguous. Mark it processed with a note so it doesn't block
           the queue.
        """
        self.ensure_one()
        if self.processed:
            return
        emp = self._find_employee()
        if not emp:
            self.write({'error': _('No employee with zk_user_id or barcode = %s') % self.pin})
            return
        Att = self.env['hr.attendance'].sudo()

        # 1. Noise filter — same swipe sent multiple times in quick succession
        recent = Att.search(
            [('employee_id', '=', emp.id)],
            order='check_in desc',
            limit=1,
        )
        if recent:
            def _near(a, b, seconds=60):
                return a and b and abs((a - b).total_seconds()) < seconds
            if (_near(recent.check_in, self.punch_time)
                    or _near(recent.check_out, self.punch_time)):
                self.write({
                    'employee_id': emp.id,
                    'attendance_id': recent.id,
                    'processed': True,
                    'error': False,
                })
                return

        # 2. If there's an open session, always close it (no timestamp guard)
        open_att = Att.search(
            [('employee_id', '=', emp.id), ('check_out', '=', False)],
            order='check_in desc',
            limit=1,
        )
        if open_att:
            # Make sure check_out is strictly after check_in (Odoo constraint)
            check_out_time = self.punch_time
            if check_out_time <= open_att.check_in:
                # Punch is earlier than or equal to the open check_in — treat
                # as a duplicate/out-of-order retry of the check_in itself.
                self.write({
                    'employee_id': emp.id,
                    'attendance_id': open_att.id,
                    'processed': True,
                    'error': False,
                })
                return
            open_att.check_out = check_out_time
            self.write({
                'employee_id': emp.id,
                'attendance_id': open_att.id,
                'processed': True,
                'error': False,
            })
            return

        # 3. Historical backfill guard — if this punch is older than the most
        # recent closed attendance, we'd be splicing into history. Skip it.
        if recent and recent.check_in and self.punch_time < recent.check_in:
            self.write({
                'employee_id': emp.id,
                'processed': True,
                'error': _('Skipped: punch is older than latest attendance'),
            })
            return

        # 4. Open a new attendance
        try:
            new_att = Att.create({
                'employee_id': emp.id,
                'check_in': self.punch_time,
            })
        except Exception as e:
            # Most likely Odoo's "hasn't checked out" guard — reload the
            # employee and surface a readable message rather than the stack trace
            self.write({
                'employee_id': emp.id,
                'error': (str(e) or 'attendance create failed')[:500],
            })
            return
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
