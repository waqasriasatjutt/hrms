# models/payment_transaction.py
import logging
from odoo import models, fields, api, _
from ..services.mirillium.api import refund_payment_by_token
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PaymentTransactionPayrillium(models.Model):
    _inherit = 'payment.transaction'

    payrillium_terminal_id = fields.Many2one(
        'payrillium.terminal',
        string="Payrillium Terminal Used",
        help="Terminal used to process this Payrillium transaction."
    )
    card_type = fields.Char(
        string="Card Type",
        help="The card type used in this transaction (CREDIT or DEBIT)"
    )
    is_duplicate = fields.Boolean(
        string="Duplicate Payment",

        help="This transaction was made using a payment link that has already been used. It should be reviewed manually."
    )
    payrillium_card_token = fields.Char(
        string="Payrillium Token",
        copy=False,
        help="Token returned by Cybersource"
    )

    invoice_ids = fields.Many2many(
        'account.move',
        help='Invoices related to this Payrillium transaction.',
        string='Invoices Related',
    )
    duplicate_status = fields.Char(
        compute='_compute_duplicate_status',
        string='',
        store=True
    )
    duplicate_icon = fields.Char(
        string='',
        compute='_compute_duplicate_icon',
        store=False
    )

    def _compute_duplicate_status(self):
        for record in self:
            record.duplicate_status = "   Duplicate" if record.is_duplicate else ""

    def _compute_duplicate_icon(self):
        for rec in self:
            rec.duplicate_icon = "  " if rec.is_duplicate else ""

    def _payrillium_form_get_tx_from_data(self, data):
        """Find a transaction based on the 'reference' from Payrillium data."""
        reference = data.get('reference')
        return self.search([('reference', '=', reference)], limit=1)

    def _payrillium_form_validate(self, data):
        """Mark the transaction as completed successfully."""
        self.ensure_one()
        self.write({
            'acquirer_reference': data.get('transaction_id'),
            'state': 'done',  # Or 'pending' if you use a delayed capture flow
        })
        return True

    @api.model
    def create_from_pos_payrillium(self, values):
        """Create a Payment Transaction record for a Payrillium payment."""
        _logger.info(
            "  [create_from_pos_payrillium] Values received: %s", values)

        provider = self.env['payment.provider'].search(
            [('code', '=', 'payrillium')], limit=1)

        if not provider:
            _logger.error("  No Payrillium payment provider found.")
            raise ValueError("No Payrillium payment provider configured.")

        terminal_id = values.get('terminal_id') or False
        transaction = self.create({
            'reference': values.get('reference'),
            'provider_reference': values.get('acquirer_reference'),
            'payment_method_id': values.get('payment_method_id'),
            'amount': values.get('amount'),
            'currency_id': self.env.company.currency_id.id,
            'partner_id': self.env.user.partner_id.id,
            'provider_id': provider.id,
            'state': values.get('state'),
            'payrillium_terminal_id': terminal_id,
            'card_type': values.get('card_type'),
            'payrillium_card_token': values.get('payrillium_card_token'),
        })

        pos_order = self.env['pos.order'].search(
            [('pos_reference', '=', values.get('order_pos_reference'))], limit=1)
        if pos_order:
            pos_payment = self.env['pos.payment'].search([
                ('pos_order_id', '=', pos_order.id),
                ('transaction_id', '=', False),
                ('amount', '=', values.get('amount')),
            ], limit=1)
            if pos_payment:
                pos_payment.write(
                    {'transaction_id': values.get('acquirer_reference')})
                _logger.info(" pos.payment updated with transaction_id")

            _logger.info(
                "  Payment transaction created successfully: ID %s", transaction.id)

        return transaction.id

    def _send_payment_request_to_terminal(self):
        self.ensure_one()
        self.write({
            'state': 'done',
            'provider_reference': self.reference or 'Manual',
        })

    def _log_message_on_linked_documents(self, message):
        """Log a message on the invoices linked to the transaction."""
        super()._log_message_on_linked_documents(message)

        # For Payrillium transactions, also log on the invoice
        for tx in self:
            if tx.provider_code == 'payrillium' and tx.invoice_ids:
                for invoice in tx.invoice_ids:
                    invoice.message_post(
                        body=message,
                        message_type='notification',
                        subtype_xmlid='payment.payment_notification'
                    )

    def _update_source_transaction_state(self):
        """Update the source transaction state and create payment if needed."""
        for tx in self:
            if tx.provider_code == 'payrillium' and tx.state == 'done':
                # Create payment if it doesn't exist
                if not tx.payment_id and tx.invoice_ids:
                    tx._create_payment_from_transaction()

    def _create_payment_from_transaction(self):
        """Create an account.payment from this transaction."""
        self.ensure_one()

        _logger.info(
            f"🔧 _create_payment_from_transaction called for transaction {self.id}")
        _logger.info(f"  - payment_id: {self.payment_id}")
        _logger.info(f"  - invoice_ids: {self.invoice_ids}")
        _logger.info(f"  - partner_id: {self.partner_id}")
        _logger.info(f"  - amount: {self.amount}")
        _logger.info(f"  - currency_id: {self.currency_id}")

        if self.payment_id:
            _logger.info(f"  - Payment already exists: {self.payment_id}")
            return self.payment_id

        if not self.invoice_ids:
            _logger.warning("  - No invoice_ids found")
            return False

        invoice = self.invoice_ids[0]
        _logger.info(f"  - Using invoice: {invoice.name} (ID: {invoice.id})")

        # Get payment method line
        payment_method_line = self.env['account.payment.method.line'].search([
            ('payment_type', '=', 'inbound'),
            ('journal_id.type', '=', 'bank')
        ], limit=1)

        _logger.info(f"  - payment_method_line: {payment_method_line}")

        if not payment_method_line:
            _logger.warning(
                "No payment method line found for Payrillium payment")
            return False

        # Create payment
        payment_vals = {
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner_id.id,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'date': fields.Date.context_today(self),
            'journal_id': payment_method_line.journal_id.id,
            'payment_method_line_id': payment_method_line.id,
            'payment_transaction_id': self.id,
            'memo': f"Payment for {invoice.name} via Payrillium",
        }

        _logger.info(f"  - Creating payment with vals: {payment_vals}")

        try:
            payment = self.env['account.payment'].sudo().create(payment_vals)
            _logger.info(f"  - Payment created: {payment.id}")

            payment.action_post()
            _logger.info(f"  - Payment posted: {payment.id}")

            # Reconcile with invoice
            (payment.move_id.line_ids + invoice.line_ids).filtered(
                lambda line: line.account_id.account_type == 'asset_receivable' and not line.reconciled
            ).reconcile()
            _logger.info(f"  - Payment reconciled with invoice")

            # Update invoice UI to show "Paid" status immediately
            invoice.invalidate_recordset(
                ['invoice_outstanding_credits_debits_widget'])
            _logger.info(f"  - Invoice UI updated to show Paid status")

            # Force UI refresh by invalidating related fields
            invoice.invalidate_recordset(
                ['payment_state', 'amount_residual', 'invoice_payments_widget'])
            _logger.info(
                f"  - Invoice payment fields invalidated for UI refresh")

            # Log payment posted message
            payment.message_post(
                body=_("The payment related to the transaction with reference %(ref)s has been posted: %(payment)s",
                       ref=self.reference,
                       payment=payment.name),
                message_type='notification',
                subtype_xmlid='account.mt_invoice_payment'
            )
            _logger.info(f"  - Message posted to payment")

            _logger.info(
                f"✅ Payment {payment.id} created and reconciled for transaction {self.id}")
            return payment

        except Exception as e:
            _logger.error(f"❌ Error creating payment: {e}")
            raise

    def _send_refund_request(self, amount_to_refund=None):
        self.ensure_one()

        if self.provider_code != "payrillium":
            return super()._send_refund_request(amount_to_refund=amount_to_refund)

        refund_tx = super()._send_refund_request(amount_to_refund=amount_to_refund)
        _logger.info("refund_tx: %s", refund_tx)

        token = self.provider_reference
        if not token:
            raise UserError("No provider_reference found to request refund.")

        result = refund_payment_by_token(
            self.provider_id, token, -refund_tx.amount)
        _logger.info("resultrefund_payment_by_token: %s", result)

        if not result.get("success"):
            refund_tx.state = "cancel"
            self.message_post(body=f"Refund failed: {result.get('message')}")
            raise UserError(f"Refund failed: {result.get('message')}")

        refund_data = result["refund_data"]
        refund_tx.provider_reference = refund_data.get("external_ref")
        refund_tx.card_type = refund_data.get("card_type")

        refund_status = refund_data.get("status", "").upper()
        if refund_status in ("AUTHORIZED", "DONE"):
            refund_tx.sudo()._set_done("Refund completed via Payrillium")

            if self.invoice_ids:
                invoice = self.invoice_ids[0].sudo()
                reversal = invoice._reverse_moves(default_values_list=[{
                    'ref': f"Refund of {invoice.name}",
                    'date': fields.Date.context_today(self),
                }], cancel=False)

                _logger.info("reversal: %s", reversal)

                refund_invoice = reversal
                refund_invoice.action_post()

                journal = self.env['account.journal'].search([
                    ('type', '=', 'bank'),
                    ('company_id', '=', self.company_id.id),
                ], limit=1)

                if not journal:
                    journal = self.env['account.journal'].search([
                        ('type', '=', 'bank'),
                        ('company_id', '=', self.company_id.id),
                    ], limit=1)

                if not journal:
                    _logger.warning(
                        "Refund journal not found. Skipping payment registration.")
                    return refund_tx

                refund_payment = self.env['account.payment'].create({
                    'partner_id': self.partner_id.id,
                    'journal_id': journal.id,
                    'payment_type': 'outbound',
                    'amount': abs(refund_tx.amount),
                    'payment_method_line_id': journal.inbound_payment_method_line_ids[:1].id,
                    'partner_type': 'customer',
                    'date': fields.Date.context_today(self),
                    'ref': f"Refund for {invoice.name}",
                })

                refund_payment.action_post()

                lines = (refund_payment.line_ids + invoice.line_ids).filtered(
                    lambda l: l.account_id == invoice.line_ids[0].account_id and l.account_id.reconcile
                )
                lines.reconcile()

        else:
            refund_tx.state = "cancel"
            refund_tx.sudo().write({
                "state": "cancel",
                "state_message": f"Refund failed: {result.get('message') or 'Unknown error'}",
            })

        return refund_tx

        # # def _send_refund_request(self, amount_to_refund=None):
        # self.ensure_one()

        # if self.provider_code != "payrillium":
        #     return super()._send_refund_request(amount_to_refund=amount_to_refund)

        # refund_tx = super()._send_refund_request(amount_to_refund=amount_to_refund)

        # _logger.info("refund_tx: %s", refund_tx)

        # token = self.provider_reference
        # if not token:
        #     raise UserError("No provider_reference found to request refund.")

        # result = refund_payment_by_token(self.provider_id, token, -refund_tx.amount)

        # _logger.info("resultrefund_payment_by_token: %s", result)

        # if not result.get("success"):
        #     refund_tx.state = "cancel"
        #     self.message_post(body=f"Refund failed: {result.get('message')}")
        #     raise UserError(f"Refund failed: {result.get('message')}")

        # refund_data = result["refund_data"]

        # refund_tx.provider_reference = refund_data.get("external_ref")
        # refund_tx.card_type = refund_data.get("card_type")

        # if refund_data.get("status").upper() == "AUTHORIZED" or refund_data.get("status").upper() == "DONE":
        #     if refund_tx and refund_tx.exists():
        #         refund_tx.sudo()._set_done("Refund completed via Payrillium")
        #         if self.payment_id:
        #             payment = self.payment_id.sudo()
        #             if payment.state not in ("cancelled", "reconciled"):
        #                 payment.cancel()
        # else:
        #     refund_tx.state = "cancel"
        #     refund_tx.sudo().write({
        #         "state": "cancel",
        #         "state_message": f"Refund failed: {result.get('message') or 'Unknown error'}",
        #     })
        # return refund_tx
