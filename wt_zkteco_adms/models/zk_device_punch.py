# -*- coding: utf-8 -*-
import logging
from datetime import timedelta

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

        Pairing rules (tuned for real-world device messiness):

        1. **Noise filter** — same swipe sent multiple times in quick succession
           (ZKTeco devices often retry a swipe 2-3 times within seconds) is
           absorbed into the most recent attendance.
        2. **Stale-session auto-close** — if there's an open attendance older
           than `device.auto_close_hours` (default 14h), it's assumed the
           employee forgot to punch out. The stale session is closed at
           `check_in + default_shift_hours` (default 9h) and THIS punch opens
           a fresh attendance. Prevents 72-hour overnight "sessions".
        3. **Normal close** — if an open session exists and is recent (<14h),
           this punch closes it. Guards against timestamps earlier than or
           equal to check_in.
        4. **Historical backfill** — if this punch is older than the most
           recent closed attendance, we do not try to splice into history.
           Marked processed with a note.
        5. **Open new** — otherwise create a new open attendance at this punch
           time.
        """
        self.ensure_one()
        if self.processed:
            return
        emp = self._find_employee()
        if not emp:
            self.write({'error': _('No employee with zk_user_id or barcode = %s') % self.pin})
            return
        Att = self.env['hr.attendance'].sudo()

        # ── 1. Noise filter ──────────────────────────────────────────────
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

        # ── 2./3. Handle any open session ────────────────────────────────
        open_att = Att.search(
            [('employee_id', '=', emp.id), ('check_out', '=', False)],
            order='check_in desc',
            limit=1,
        )
        if open_att:
            device = self.device_id
            auto_close_hours = device.auto_close_hours or 14.0
            default_shift = device.default_shift_hours or 9.0
            gap = (self.punch_time - open_att.check_in).total_seconds() / 3600.0

            if auto_close_hours and gap >= auto_close_hours:
                # STALE SESSION — employee forgot to punch out yesterday.
                # Close the stale session at check_in + default_shift,
                # then open a new attendance for this punch.
                stale_close = open_att.check_in + timedelta(hours=default_shift)
                try:
                    open_att.write({'check_out': stale_close})
                    _logger.info(
                        "zk.device.punch: auto-closed stale attendance %s "
                        "(employee=%s, check_in=%s) — gap was %.1fh",
                        open_att.id, emp.name, open_att.check_in, gap,
                    )
                except Exception as e:
                    _logger.warning("Auto-close failed on attendance %s: %s",
                                    open_att.id, e)
                    self.write({
                        'employee_id': emp.id,
                        'error': _('Auto-close failed: %s') % e,
                    })
                    return
                # Fall through to the "open new attendance" branch below
            else:
                # NORMAL CLOSE — close the open session with this punch
                check_out_time = self.punch_time
                if check_out_time <= open_att.check_in:
                    # Punch is earlier than or equal to check_in — duplicate
                    # retry of the check_in itself. Absorb silently.
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

        # ── 4. Historical backfill guard ─────────────────────────────────
        if recent and recent.check_in and self.punch_time < recent.check_in:
            self.write({
                'employee_id': emp.id,
                'processed': True,
                'error': _('Skipped: punch is older than latest attendance'),
            })
            return

        # ── 5. Open a new attendance ─────────────────────────────────────
        try:
            new_att = Att.create({
                'employee_id': emp.id,
                'check_in': self.punch_time,
            })
        except Exception as e:
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
