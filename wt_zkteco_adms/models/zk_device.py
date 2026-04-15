# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class ZkDevice(models.Model):
    _name = 'zk.device'
    _description = 'ZKTeco Biometric Device'
    _order = 'name'

    name = fields.Char(required=True)
    serial_number = fields.Char(
        'Serial Number', required=True, index=True, copy=False,
        help='Matches the SN the device sends in /iclock/cdata query string.',
    )
    location = fields.Char(help='Physical location — free text')
    is_active = fields.Boolean(
        default=True,
        help='If off, incoming punches are logged but dropped (no hr.attendance written). '
             'Newly auto-registered devices start inactive — vet them first.',
    )
    last_seen = fields.Datetime(readonly=True)
    timezone_offset = fields.Integer(
        'Timezone Offset (hours)', default=5,
        help='Timezone the device reports its timestamps in (hours east of UTC). '
             'Pakistan = 5, Saudi Arabia = 3, UAE = 4. '
             'Used to convert device-local punch times into UTC before storing. '
             'Also sent back to the device in the config handshake so its clock '
             'stays in sync.',
    )
    auto_close_hours = fields.Float(
        'Auto-Close Stale Sessions After (h)', default=14.0,
        help='If an employee has an open attendance older than this many hours '
             'when a new punch arrives, the open session is auto-closed at '
             'check_in + default_shift_hours instead of merging the new punch '
             'into it. Prevents 72-hour attendances caused by missed check-outs. '
             'Set to 0 to disable.',
    )
    default_shift_hours = fields.Float(
        'Default Shift Length (h)', default=9.0,
        help='Used when auto-closing stale sessions — the stale session gets '
             'check_out = check_in + this many hours.',
    )
    note = fields.Text()
    company_id = fields.Many2one('res.company', default=lambda s: s.env.company)

    punch_ids = fields.One2many('zk.device.punch', 'device_id')
    punch_count = fields.Integer(compute='_compute_counts', store=False)
    unmatched_count = fields.Integer(compute='_compute_counts', store=False)
    unprocessed_count = fields.Integer(compute='_compute_counts', store=False)

    _sql_constraints = [
        ('uniq_serial', 'unique(serial_number)', 'Serial number must be unique.'),
    ]

    @api.depends('punch_ids', 'punch_ids.employee_id', 'punch_ids.processed')
    def _compute_counts(self):
        for rec in self:
            rec.punch_count = len(rec.punch_ids)
            rec.unmatched_count = len(rec.punch_ids.filtered(lambda p: not p.employee_id))
            rec.unprocessed_count = len(rec.punch_ids.filtered(lambda p: not p.processed))

    def action_view_punches(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Punches — %s') % self.name,
            'res_model': 'zk.device.punch',
            'view_mode': 'list,form',
            'domain': [('device_id', '=', self.id)],
            'context': {'default_device_id': self.id},
        }

    def action_reprocess_unprocessed(self):
        """Re-run attendance pairing for every still-unprocessed punch.

        Useful after fixing an employee's zk_user_id mapping: the old
        unmatched punches will get picked up on the next reprocess.
        """
        for rec in self:
            punches = rec.punch_ids.filtered(lambda p: not p.processed).sorted('punch_time')
            for p in punches:
                p._process_to_attendance()
        return True

    def action_ping_url(self):
        """Open a notification with the device-facing URL to paste into the Cloud Server setting."""
        self.ensure_one()
        base = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('ADMS Endpoint'),
                'message': _(
                    "Set on device → Menu → Comm → Cloud Server Setting:\n"
                    "  Server Address: %s\n"
                    "  Path: /iclock/\n"
                    "  Port: 80 or 443\n"
                    "  Enable Domain Name: ON if using HTTPS\n\n"
                    "Quick sanity check from the device's network:\n"
                    "  curl %s/iclock/ping"
                ) % (base, base),
                'type': 'info',
                'sticky': True,
            },
        }
