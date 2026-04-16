import logging
from odoo import models, fields, api
from odoo.exceptions import UserError
from ..controllers.main import build_url, build_header_hash, deep_clean_payload, log_payrillium_event
from datetime import datetime
import json
import requests


_logger = logging.getLogger(__name__)


class PayrilliumTerminal(models.Model):
    _name = 'payrillium.terminal'
    _description = 'Payrillium Terminal'

    name = fields.Char(string="Name", required=True)
    serial = fields.Char(string="Serial Number")
    last_session_id = fields.Many2one(
        'pos.session', string="Last Session", compute='_compute_last_session', store=True)

    pos_config_name = fields.Char(
        string="POS Config", compute='_compute_last_session', store=True)
    pos_config_id = fields.Many2one(
        'pos.config',
        string='POS Config'
    )

    def _compute_last_session(self):
        _logger.info(" Starting _compute_last_session for all terminals...")
        for terminal in self:
            _logger.info(f"  Terminal: {terminal.name} (ID: {terminal.id})")

            terminal.last_session_id = False
            terminal.pos_config_name = False

            pos_config = self.env['pos.config'].search([
                ('payrillium_terminal_id', '=', terminal.id)
            ], limit=1)

            if pos_config:
                _logger.info(
                    f"  POS Config found: {pos_config.name} (ID: {pos_config.id})")

                session = self.env['pos.session'].search([
                    ('config_id', '=', pos_config.id),
                    ('state', 'in', ['opened', 'opening_control', 'closed'])
                ], order='id desc', limit=1)

                if session:
                    _logger.info(
                        f"  Session found: {session.name} (State: {session.state})")
                    terminal.last_session_id = session.id
                    terminal.pos_config_name = pos_config.name
                else:
                    _logger.warning(
                        f"   No session found for POS Config {pos_config.name}")
            else:
                _logger.warning(
                    f"   No POS Config found for terminal {terminal.name}")

        _logger.info(" Finished _compute_last_session.")

    @api.model
    def _check_terminal_core(self, terminal_serial):
        try:
            if not terminal_serial:
                return {"status": "error", "message": "No terminal serial provided"}

            payload = {"data": {}}
            url = build_url(terminal_serial, "local", "test")
            log_payrillium_event(
                "missing", "check_terminal", "request", payload)

            timestamp = int(datetime.utcnow().timestamp())
            payload = deep_clean_payload(payload)
            auth_hash = build_header_hash(self.env, payload, timestamp)
            request_body = json.dumps(payload, separators=(",", ":"))

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Basic {auth_hash}",
                "timestamp": str(timestamp),
            }

            _logger.info("Check terminal payload=%s, ts=%s",
                         request_body, timestamp)
            resp = requests.post(url, headers=headers, json={
                                 "data": request_body})
            resp.raise_for_status()
            data = resp.json()

            log_payrillium_event("missing", "check_terminal",
                                 "response", data, success=True)
            return {"status": "success", "data": data}
        except Exception as e:
            log_payrillium_event("missing", "check_terminal",
                                 "response", None, success=False, error_message=str(e))
            return {"status": "error", "message": str(e)}

    def action_check_terminal(self):
        self.ensure_one()
        if not self.serial:
            raise UserError("Terminal has no serial number configured.")
        _logger.info("Checking terminal (backend direct): %s (%s)",
                     self.name, self.serial)

        result = self.env['payrillium.terminal']._check_terminal_core(
            self.serial)
        ok = result.get("status") == "success" and (result.get(
            "data", {}).get("data", {}).get("success") is True)

        if ok:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {'title': 'Terminal Connected Successfully',
                           'message': f"Terminal {self.name} ({self.serial}) is online.",
                           'type': 'success', 'sticky': False}
            }
        else:
            msg = result.get('message') or 'Unknown error'
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {'title': 'Connection Error',
                           'message': f"Unable to connect to terminal: {msg}",
                           'type': 'danger', 'sticky': True}
            }

    @api.model
    def _reset_terminal_core(self, terminal_serial):
        try:
            if not terminal_serial:
                return {"status": "error", "message": "No terminal ID provided"}

            payload = {"data": {}}
            url = build_url(terminal_serial, "payment", "abort")
            timestamp = int(datetime.utcnow().timestamp())
            payload = deep_clean_payload(payload)
            auth_hash = build_header_hash(self.env, payload, timestamp)
            request_body = json.dumps(payload, separators=(",", ":"))
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Basic {auth_hash}",
                "timestamp": str(timestamp),
            }

            log_payrillium_event(
                "missing", "reset_terminal", "request", request_body)
            resp = requests.post(url, headers=headers, json={
                                 "data": request_body})
            resp.raise_for_status()
            data = resp.json()

            log_payrillium_event("missing", "reset_terminal",
                                 "response", data, success=True)
            return {"status": "success", "data": data}
        except Exception as e:
            log_payrillium_event("missing", "reset_terminal",
                                 "response", None, success=False, error_message=str(e))
            return {"status": "error", "message": str(e)}

    def action_abort_terminal(self):
        self.ensure_one()
        if not self.serial:
            raise UserError("Terminal has no serial number configured.")

        _logger.info("Reset terminal (backend direct): %s (%s)",
                     self.name, self.serial)

        result = self.env['payrillium.terminal']._reset_terminal_core(
            self.serial)
        top_success = result.get("status") == "success"
        data = result.get("data") or {}
        data_success = (data.get("data") or {}).get("success")

        if top_success and data_success:
            message = f"Terminal {self.name} ({self.serial}) was reset successfully"
            msg_type = "success"
        elif top_success and not data_success:
            reason = (data.get("data") or {}).get(
                "reason", "No reason provided")
            message = (f"No operation to abort on terminal {self.name} ({self.serial})\n"
                       f"Reason: {reason}")
            msg_type = "warning"
        else:
            message = result.get("message", "Unknown error")
            msg_type = "danger"

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Terminal Reset Result',
                'message': message,
                'type': msg_type,
                'sticky': False,
            }
        }

    def action_unlink_terminal(self):
        if len(self) != 1:
            raise UserError(
                "Please select exactly one terminal to perform this action.")
        for terminal in self:
            _logger.info(
                f" Unlinking terminal: {terminal.name} (ID: {terminal.id})")
            if terminal.pos_config_id:
                active_session = self.env['pos.session'].search([
                    ('config_id', '=', terminal.pos_config_id.id),
                    ('state', 'in', ['opened', 'opening_control']),
                ], limit=1)

                if active_session:
                    _logger.warning(
                        f"  Cannot unlink terminal; session {active_session.name} is still active.")
                    raise UserError(
                        f"Cannot unlink terminal '{terminal.name}' because session '{active_session.name}' is still open or in opening control."
                    )

            if terminal.pos_config_id:
                _logger.info(
                    f"  Removing terminal {terminal.name} from POS Config {terminal.pos_config_id.name}")

                pos_config = terminal.pos_config_id
                pos_config.payrillium_terminal_id = False

                terminal.write({
                    'pos_config_id': False,
                    'pos_config_name': False,
                    'last_session_id': False,
                })

                _logger.info(
                    f"  Terminal {terminal.name} unlinked successfully.")
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Terminal Unlinked',
                        'message': 'The terminal was successfully unlinked.',
                        'type': 'success',
                        'sticky': False,
                        'next': {
                            'type': 'ir.actions.client',
                            'tag': 'reload',
                        }
                    }
                }
            else:
                _logger.warning(
                    f"   Terminal {terminal.name} is not linked to any POS Config.")
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Not Linked',
                        'message': 'The terminal is not linked to any POS Config.',
                        'type': 'warning',
                        'sticky': True,
                    }
                }

    def action_delete_terminal(self):
        if len(self) != 1:
            raise UserError(
                "Please select exactly one terminal to perform this action.")
        for terminal in self:
            _logger.info(
                f" DELETE Terminal requested: {terminal.name} (Serial: {terminal.serial})")

    def name_get(self):
        result = []
        for terminal in self:
            serial_suffix = terminal.serial[-4:] if terminal.serial and len(
                terminal.serial) >= 4 else ""
            label = f"{terminal.name} - {serial_suffix}" if serial_suffix else terminal.name
            _logger.info(f" name_get called for: {label}")
            result.append((terminal.id, label))
        return result
