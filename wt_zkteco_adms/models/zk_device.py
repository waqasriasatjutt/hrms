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
        'Timezone Offset (hours)', default=3,
        help='Sent to the device in the config handshake. Saudi Arabia = 3.',
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
