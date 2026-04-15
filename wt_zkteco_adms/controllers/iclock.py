# -*- coding: utf-8 -*-
"""ADMS (Push SDK) controller for ZKTeco biometric devices.

The device calls these endpoints over HTTP on a configurable interval:

  GET  /iclock/cdata?SN=<sn>&options=all&pushver=2.2.14   → config handshake
  POST /iclock/cdata?SN=<sn>&table=ATTLOG&Stamp=<ts>      → attendance rows
  POST /iclock/cdata?SN=<sn>&table=OPERLOG&Stamp=<ts>     → user/FP changes
  GET  /iclock/getrequest?SN=<sn>                         → command poll
  POST /iclock/devicecmd?SN=<sn>                          → command result

All responses are plain text. The device strictly checks for an
"OK" / "OK: <n>" body on push endpoints — anything else is treated as
a failure and the device will resend on the next cycle.
"""
import logging
from datetime import datetime, timedelta

from odoo import fields, http
from odoo.http import Response, request

_logger = logging.getLogger(__name__)


def _text(body, status=200):
    """Plain-text response helper."""
    if isinstance(body, bytes):
        body = body.decode('utf-8', errors='replace')
    return Response(body, status=status, content_type='text/plain; charset=utf-8')


class IClockController(http.Controller):
    """Endpoints consumed by ZKTeco devices running the ADMS / Push SDK firmware."""

    # ── Helpers ─────────────────────────────────────────────────────────────
    def _get_device(self, sn, touch=True):
        """Fetch or auto-register the device by serial number.

        Unknown devices are created as inactive so an admin can vet them
        before enabling attendance write-through.
        """
        if not sn:
            return None
        Device = request.env['zk.device'].sudo()
        dev = Device.search([('serial_number', '=', sn)], limit=1)
        if not dev:
            dev = Device.create({
                'serial_number': sn,
                'name': 'ZK Device %s' % sn,
                'is_active': False,
            })
            _logger.info("ADMS: new device registered SN=%s (inactive)", sn)
        if touch:
            dev.write({'last_seen': fields.Datetime.now()})
        return dev

    def _parse_attlog_body(self, body, device):
        """Yield parsed dicts from an ATTLOG body.

        ZKTeco format (tab-separated, one row per line):
            <pin>\\t<YYYY-MM-DD HH:MM:SS>\\t<status>\\t<verify>\\t<workcode>\\t<r1>\\t<r2>
        Extra/missing trailing columns are tolerated.

        IMPORTANT: the device reports timestamps in its **local** time
        (what the employee sees on the screen). Odoo stores all datetimes
        as UTC. We subtract the device's timezone offset here so what gets
        written to zk_device_punch.punch_time is proper UTC. Then Odoo's UI
        will display it correctly in the user's timezone.
        """
        tz_offset_hours = device.timezone_offset or 0
        tz_delta = timedelta(hours=tz_offset_hours)
        for raw_line in (body or '').replace('\r\n', '\n').split('\n'):
            line = raw_line.strip()
            if not line:
                continue
            parts = line.split('\t')
            if len(parts) < 2:
                continue
            pin = parts[0].strip()
            ts_str = parts[1].strip()
            try:
                ts_local = datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                _logger.warning("ADMS: bad timestamp %r on line %r", ts_str, line)
                continue
            ts_utc = ts_local - tz_delta
            yield {
                'pin': pin,
                'punch_time': ts_utc,
                'status': parts[2].strip() if len(parts) > 2 else '',
                'verify': parts[3].strip() if len(parts) > 3 else '',
                'workcode': parts[4].strip() if len(parts) > 4 else '',
            }

    # ── /iclock/cdata — config GET + data POST ──────────────────────────────
    @http.route('/iclock/cdata', type='http', auth='public', csrf=False,
                methods=['GET', 'POST'], save_session=False)
    def cdata(self, **kwargs):
        sn = kwargs.get('SN') or ''
        device = self._get_device(sn)
        if not device:
            # No SN → device will retry; return minimal OK
            return _text('OK\n')

        method = request.httprequest.method
        table = (kwargs.get('table') or '').upper()

        if method == 'GET':
            # Config handshake — the exact keys the device looks for
            lines = [
                'GET OPTION FROM: %s' % sn,
                'ATTLOGStamp=None',
                'OPERLOGStamp=None',
                'ErrorDelay=30',
                'Delay=10',
                'TransTimes=00:00;14:05',
                'TransInterval=1',
                'TransFlag=TransData AttLog OpLog EnrollUser ChgUser EnrollFP ChgFP UserPic',
                'TimeZone=%d' % (device.timezone_offset or 5),
                'Realtime=1',
                'Encrypt=None',
            ]
            return _text('\r\n'.join(lines) + '\r\n')

        # POST — data from device.
        # Some ZKTeco firmwares send body as text/plain (then werkzeug leaves
        # the raw stream intact); others omit Content-Type or send it as
        # application/x-www-form-urlencoded, and Odoo's dispatcher has already
        # parsed it into kwargs by the time we get here. Handle both.
        raw = request.httprequest.get_data(as_text=True) or ''
        if not raw and kwargs:
            # Reconstruct from form-parsed kwargs: when the body is
            # "1\t2026-04-15 08:00:00\t0\t1..." werkzeug's form parser sees
            # the whole thing as a single key with empty value. Rebuild it.
            rebuilt = []
            for k, v in kwargs.items():
                if k in ('SN', 'table', 'Stamp', 'options', 'pushver', 'language'):
                    continue
                rebuilt.append('%s=%s' % (k, v) if v else k)
            raw = '\n'.join(rebuilt)

        if table == 'ATTLOG':
            count = self._handle_attlog(device, raw)
            return _text('OK: %d\n' % count)

        if table == 'OPERLOG':
            self._handle_operlog(device, raw)
            return _text('OK\n')

        # Unknown table — log and ack
        _logger.info("ADMS: ignoring table=%s from SN=%s (body=%d bytes)",
                     table or '(none)', sn, len(raw))
        return _text('OK\n')

    def _handle_attlog(self, device, body):
        """Insert ATTLOG rows as zk.device.punch, return count written."""
        if not device.is_active:
            _logger.info("ADMS: ATTLOG from INACTIVE device SN=%s dropped (%d bytes)",
                         device.serial_number, len(body or ''))
            # Still return the count so the device clears its buffer
            return sum(1 for _row in self._parse_attlog_body(body, device))

        Punch = request.env['zk.device.punch'].sudo()
        count = 0
        for row in self._parse_attlog_body(body, device):
            # Idempotent: skip if this exact punch already exists
            exists = Punch.search_count([
                ('device_id', '=', device.id),
                ('pin', '=', row['pin']),
                ('punch_time', '=', row['punch_time']),
            ])
            if exists:
                count += 1
                continue
            try:
                Punch.create({
                    'device_id': device.id,
                    'pin': row['pin'],
                    'punch_time': row['punch_time'],
                    'status': row['status'],
                    'verify': row['verify'],
                    'workcode': row['workcode'],
                })
                count += 1
            except Exception as e:
                _logger.warning("ADMS: failed to insert punch %s/%s: %s",
                                row['pin'], row['punch_time'], e)
        _logger.info("ADMS: ATTLOG SN=%s wrote %d punches", device.serial_number, count)
        return count

    def _handle_operlog(self, device, body):
        """OPERLOG covers user/fingerprint/face changes.

        We log the raw payload for now — syncing back user metadata to
        hr.employee is a future enhancement (see zk.device.command TODO).
        """
        snippet = (body or '')[:500].replace('\n', ' | ')
        _logger.info("ADMS OPERLOG SN=%s bytes=%d first=%r",
                     device.serial_number, len(body or ''), snippet)

    # ── /iclock/getrequest — command polling ────────────────────────────────
    @http.route('/iclock/getrequest', type='http', auth='public', csrf=False,
                methods=['GET'], save_session=False)
    def getrequest(self, **kwargs):
        sn = kwargs.get('SN') or ''
        self._get_device(sn)
        # No pending commands for now. Future: pop from zk.device.command queue.
        return _text('OK\n')

    # ── /iclock/devicecmd — command result ──────────────────────────────────
    @http.route('/iclock/devicecmd', type='http', auth='public', csrf=False,
                methods=['POST'], save_session=False)
    def devicecmd(self, **kwargs):
        sn = kwargs.get('SN') or ''
        self._get_device(sn)
        body = request.httprequest.get_data(as_text=True) or ''
        _logger.info("ADMS devicecmd SN=%s body=%r", sn, body[:300])
        return _text('OK\n')

    # ── /iclock/ping — sanity check ─────────────────────────────────────────
    @http.route('/iclock/ping', type='http', auth='public', csrf=False,
                methods=['GET'], save_session=False)
    def ping(self, **kwargs):
        return _text('OK wt_zkteco_adms\n')
