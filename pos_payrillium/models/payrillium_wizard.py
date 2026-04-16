# Used to handle configuration wizard functionality
from ..config import PAYMENT_METHOD_NAME, PAYMENT_METHOD_COLOR, PAYMENT_METHOD_ICON
from odoo import models, fields, api
from odoo.exceptions import UserError
import logging
from ..services.mirillium import get_terminals_from_token, sync_existing_payment_links

_logger = logging.getLogger(__name__)


class PayrilliumWizard(models.TransientModel):
    _name = 'payrillium.wizard'
    _description = 'Wizard to configure Payrillium'

    token = fields.Char(string="Token", required=False)
    account_id = fields.Many2one(
        'account.account',
        string="Payment Account",
        required=False,
        domain=[
            ('account_type', 'in', ['asset_cash', 'bank']),
            ('deprecated', '=', False)
        ],
        help="This account will be used as the 'Outstanding Payments/Receipts' account. It must be of type 'Cash' or 'Bank' and be reconciliable."
    )
    receivable_account_id = fields.Many2one(
        'account.account',
        string="Receivable Account",
        required=False,
        domain=[
            ('account_type', '=', 'asset_receivable'),
            ('reconcile', '=', True),
            ('deprecated', '=', False)
        ],
        help="Account used for POS counterpart. Must be type 'Receivable'."
    )

    @api.model
    def check_and_open_wizard(self, *args, **kwargs):
        _logger.info(
            " Executing check_and_open_wizard with args: %s, kwargs: %s", args, kwargs)
        config = self.env['payrillium.config'].search([], limit=1)
        if not config or not config.token:
            _logger.info(" No configuration found, opening wizard")
            action = self.env.ref(
                'pos_payrillium.action_payrillium_wizard').read()[0]
            return action
        _logger.info(" Configuration already exists with token")
        return False

    def _clean_duplicate_providers(self):
        _logger.info("  Looking for duplicate Payrillium providers...")

        # Search all providers with the same code
        providers = self.env['payment.provider'].with_context(active_test=False).search([
            ('code', '=', 'payrillium'),
            ('company_id', '=', self.env.company.id)
        ], order='create_date desc')  # most recent first

        if not providers:
            return None

        # 1. Find the first one with transactions
        for provider in providers:
            tx_count = self.env['payment.transaction'].search_count([
                ('provider_id', '=', provider.id)
            ])
            if tx_count > 0:
                _logger.info(
                    f" Using provider with transactions: {provider.name} (ID: {provider.id})")
                return provider

        # 2. If none have transactions, use the most recent one
        _logger.info(
            f"  Using most recent provider without transactions: {providers[0].name} (ID: {providers[0].id})")
        return providers[0]

    def submit_token(self):
        # --- VALIDATE TERMINAL STATE BEFORE STARTING ---
        for terminal in self.env['payrillium.terminal'].search([]):
            if terminal.pos_config_id:
                active_session = self.env['pos.session'].search([
                    ('config_id', '=', terminal.pos_config_id.id),
                    ('state', 'in', ['opened', 'opening_control']),
                ], limit=1)
                if active_session:
                    raise UserError(
                        f"Cannot update configuration because terminal '{terminal.name}' is assigned to POS config '{terminal.pos_config_id.name}' "
                        f"which has an active session '{active_session.name}'. Please close the session first."
                    )
        try:
            # Validate that required fields are filled
            if not self.token:
                raise UserError(
                    "Token is required. Please enter your Payrillium API token.")
            if not self.account_id:
                raise UserError(
                    "Payment Account is required. Please select an account.")
            if not self.receivable_account_id:
                raise UserError(
                    "Receivable Account is required. Please select an account.")

            token = self.token.strip()

            if not token or len(token) < 4:
                raise UserError(
                    "Token is too short. Please enter a valid Payrillium API token.")

            if not all(c.isalnum() or c in '-_' for c in token):
                raise UserError(
                    "Token contains invalid characters. Please enter a valid Payrillium API token.")

            _logger.info("Received token in wizard: %s****",
                         token[:4] if token and len(token) > 4 else "****")

            if token == "INVALID":
                raise UserError("Invalid Token")

            response = get_terminals_from_token(token)
            _logger.info("Response: %s", response)

            if not response.get("success", False):
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": "Token Validation Failed",
                        "message": response.get("message", "Unknown Error"),
                        "type": "danger",
                        "sticky": False,
                    }
                }

            terminals = response.get("terminals", [])
            merchant_id = response.get("merchant_id")
            secret_key = response.get("secret_key")
            pbl_developer_id = response.get("pbl_developer_id")
            pbl_solution_id = response.get("pbl_solution_id")
            pbl_request_phone = response.get("pbl_request_phone")
            pbl_request_shipping = response.get("pbl_request_shipping")
            config = self.env['payrillium.config'].search([], limit=1)
            is_update = bool(config and config.installed)

            if not is_update:
                provider = self._clean_duplicate_providers()
                if not provider:
                    provider = self.env['payment.provider'].create({
                        'name': 'Payrillium Terminal',
                        'code': 'payrillium',
                        'state': 'disabled',
                        'company_id': self.env.company.id,
                    })
            else:
                provider = self.env['payment.provider'].search([
                    ('code', '=', 'payrillium'),
                    ('company_id', '=', self.env.company.id),
                ], limit=1)
                if not provider:
                    raise UserError("No Payrillium provider found for update.")

            deleted_terminals, skipped_terminals = self._synchronize_terminals(
                terminals)

            account = self.env['account.account'].search([
                ('code', '=', '101401')
            ], limit=1)
            if not account:
                account = self.env['account.account'].create({
                    'name': 'Payrillium Bridge Account',
                    'code': '101401',
                    'account_type': 'asset_cash',
                    'reconcile': True,
                })

            journal = self.env['account.journal'].with_context(active_test=False).search([
                ('code', '=', 'PAYR'), ('company_id', '=', self.env.company.id)
            ], limit=1)
            if not journal:
                journal = self.env['account.journal'].create({
                    'name': 'Payrillium Journal',
                    'type': 'bank',
                    'code': 'PAYR',
                    'company_id': self.env.company.id,
                    'default_account_id': account.id,
                })
            else:
                updates = {}
                if not journal.active:
                    updates['active'] = True
                if 'Archived' in journal.name:
                    updates['name'] = 'Payrillium Journal'
                if journal.default_account_id != self.account_id:
                    updates['default_account_id'] = self.account_id.id
                if updates:
                    journal.write(updates)

            if not provider:
                provider = self.env['payment.provider'].create({
                    'name': 'Payrillium Terminal',
                    'code': 'payrillium',
                    'state': 'disabled',
                    'company_id': self.env.company.id,
                })

            payment_method = self.env['account.payment.method'].search([
                ('payment_type', '=', 'inbound'), ('name', 'ilike', 'Manual')
            ], limit=1)
            if not payment_method:
                raise UserError("No inbound payment method found.")

            existing_lines = self.env['account.payment.method.line'].search([
                ('journal_id', '=', journal.id),
                ('payment_method_id', '=', payment_method.id)
            ])
            if existing_lines:
                existing_lines.write({
                    'name': 'Payrillium Manual In',
                    'payment_provider_id': provider.id,
                    'payment_account_id': self.account_id.id,
                    'sequence': 10,
                })
            else:
                self.env['account.payment.method.line'].create({
                    'name': 'Payrillium Manual In',
                    'journal_id': journal.id,
                    'payment_method_id': payment_method.id,
                    'payment_provider_id': provider.id,
                    'payment_account_id': self.account_id.id,
                    'sequence': 10,
                })

            if provider.state != 'enabled':
                provider.write({'state': 'enabled'})

            if is_update and provider:
                tokens = self.env['payment.token'].with_context(active_test=False).search([
                    ('provider_id', '=', provider.id),
                    ('active', '=', True)
                ])
                _logger.info("Found %s active tokens for provider %s",
                             len(tokens), provider.id)

            payment_method_code = "payrillium"
            existing_method = self.env['payment.method'].with_context(active_test=False).search([
                ('code', '=', payment_method_code)
            ], limit=1)

            if not existing_method:
                self.env['payment.method'].create({
                    'name': PAYMENT_METHOD_NAME,
                    'code': payment_method_code,
                    'sequence': 1000,
                    'active': True,
                })
            else:
                updates = {}
                if not existing_method.active:
                    updates["active"] = True
                # if existing_method.primary_payment_method_id.id != provider.id:
                #     updates["primary_payment_method_id"] = provider.id
                if updates:
                    existing_method.write(updates)

            existing = self.env['pos.payment.method'].with_context(active_test=False).search([
                ('name', '=', PAYMENT_METHOD_NAME)
            ], limit=1)

            if not existing:
                self.env['pos.payment.method'].create({
                    'name': PAYMENT_METHOD_NAME,
                    'journal_id': journal.id,
                    'receivable_account_id': self.receivable_account_id.id,
                    'outstanding_account_id': self.account_id.id,
                    'use_payment_terminal': 'payrillium',
                    'payrillium_color': PAYMENT_METHOD_COLOR,
                    'payrillium_icon': PAYMENT_METHOD_ICON,
                    'payment_provider_id': provider.id,
                })
            else:
                updates = {}
                if not existing.active:
                    updates['active'] = True
                if existing.receivable_account_id.id != self.receivable_account_id.id:
                    updates['receivable_account_id'] = self.receivable_account_id.id
                if not existing.outstanding_account_id or existing.outstanding_account_id.id != self.account_id.id:
                    updates['outstanding_account_id'] = self.account_id.id
                if not existing.payment_provider_id or existing.payment_provider_id.id != provider.id:
                    updates['payment_provider_id'] = provider.id
                if updates:
                    existing.write(updates)

            config = self.env['payrillium.config'].search([], limit=1)
            values = {
                'token': token,
                'installed': True,
                'merchant_id': merchant_id,
                'secret_key': secret_key,
                'pbl_developer_id': pbl_developer_id,
                'pbl_solution_id': pbl_solution_id,
                'pbl_request_phone': pbl_request_phone,
                'pbl_request_shipping': pbl_request_shipping,
                'receivable_account_id': self.receivable_account_id.id,
                'outstanding_account_id': self.account_id.id
            }
            if config:
                config.write(values)
            else:
                self.env['payrillium.config'].create(values)
            # Build terminal names for user notification
            terminal_names = ", ".join([t["name"] for t in terminals])

            # Build message with synchronized and deleted terminals
            message_parts = [f"Terminals synchronized: {terminal_names}"]

            if deleted_terminals:
                deleted_names = ", ".join(deleted_terminals)
                message_parts.append(f"Terminals removed: {deleted_names}")

            if skipped_terminals:
                skipped_names = ", ".join(skipped_terminals)
                message_parts.append(
                    f"Terminals skipped (active session): {skipped_names}")

            message = " | ".join(message_parts)

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Payrillium Synchronization Complete",
                    "message": message,
                    "sticky": False,
                    "type": "success",
                    "next": {"type": "ir.actions.act_window_close"},
                },
            }
        except Exception as e:
            _logger.error("Error submitting token: %s", str(e))
            raise UserError("An error occurred while submitting token.")

    def _synchronize_terminals(self, terminals):
        TerminalModel = self.env['payrillium.terminal'].sudo()
        existing_terminals = {t.serial: t for t in TerminalModel.search([])}
        incoming_serials = {t["serial"] for t in terminals}
        deleted_terminals = []
        skipped_terminals = []

        for serial, terminal_obj in existing_terminals.items():
            if serial not in incoming_serials:
                if terminal_obj.pos_config_id:
                    active_session = self.env['pos.session'].search([
                        ('config_id', '=', terminal_obj.pos_config_id.id),
                        ('state', 'in', ['opened', 'opening_control']),
                    ], limit=1)
                    if active_session:
                        _logger.warning(
                            f"Terminal {terminal_obj.name} (serial: {serial}) no longer exists in shopnet, "
                            f"but cannot be deleted because POS config '{terminal_obj.pos_config_id.name}' "
                            f"has an active session '{active_session.name}'. Skipping deletion.")
                        skipped_terminals.append(terminal_obj.name)
                        continue

                    _logger.info(
                        f"Terminal {terminal_obj.name} (serial: {serial}) no longer exists in shopnet. "
                        f"Removing from POS Config '{terminal_obj.pos_config_id.name}' before deletion.")
                    pos_config = terminal_obj.pos_config_id
                    pos_config.payrillium_terminal_id = False
                    terminal_obj.write({
                        'pos_config_id': False,
                        'pos_config_name': False,
                        'last_session_id': False,
                    })

                _logger.info(
                    f"Deleting terminal {terminal_obj.name} (serial: {serial}) because it no longer exists in shopnet.")
                deleted_terminals.append(terminal_obj.name)
                terminal_obj.unlink()

        for terminal in terminals:
            serial = terminal["serial"]
            name = terminal["name"]
            last4 = serial[-4:] if serial and len(serial) >= 4 else ""
            display_name = f"{name} - {last4}" if last4 else name

            if serial in existing_terminals:
                existing = existing_terminals[serial]
                updates = {}
                if existing.name != display_name:
                    updates['name'] = display_name
                if updates:
                    existing.write(updates)
            else:
                TerminalModel.create({
                    "name": display_name,
                    "serial": serial
                })

        return deleted_terminals, skipped_terminals
