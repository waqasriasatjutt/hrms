from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class PosOrder(models.Model):
    _inherit = 'pos.order'

    converted_currency_total = fields.Float(
        string="Converted Currency Total"
    )
    converted_currency_change = fields.Float(
        string="Converted Currency Change"
    )
    converted_currency_symbol = fields.Char(
        string="Converted Currency Symbol"
    )

    @api.model
    def _payment_fields(self, order, ui_paymentline):
        """Prepare and return a dictionary containing payment fields from the
         user interface payment line.
        params:
        order (pos.order): The POS order to which the payment belongs.
        ui_paymentline (dict): Payment information from the user interface."""
        return {
            'amount': ui_paymentline['amount'] or 0.0,
            'payment_date': ui_paymentline['name'],
            'payment_method_id': ui_paymentline['payment_method_id'],
            'card_type': ui_paymentline.get('card_type'),
            'cardholder_name': ui_paymentline.get('cardholder_name'),
            'transaction_id': ui_paymentline.get('transaction_id'),
            'payment_status': ui_paymentline.get('payment_status'),
            'ticket': ui_paymentline.get('ticket'),
            'pos_order_id': order.id,
            'payment_currency': ui_paymentline.get('payment_currency'),
            'currency_amount': ui_paymentline.get('currency_amount')
        }

    @api.model
    def _order_fields(self, ui_order):
        order_fields = super(PosOrder, self)._order_fields(ui_order)
        order_fields['converted_currency_total'] = ui_order.get('converted_currency_total', 0.0)
        order_fields['converted_currency_change'] = ui_order.get('converted_currency_change', 0.0)
        order_fields['converted_currency_symbol'] = ui_order.get('converted_currency_change', '')
        return order_fields

    def get_total_payment_currency(self, session_id):
        return self.env['pos.payment'].read_group(
            [('pos_order_id.session_id', '=', session_id)],
            ['currency_amount', 'payment_currency'],
            groupby=['payment_currency']
        )

    # Override Existing Methods
    def _process_payment_lines(self, pos_order, order, pos_session, draft):
        """Create account.bank.statement.lines from the dictionary given to the parent function.

        If the payment_line is an updated version of an existing one, the existing payment_line will first be
        removed before making a new one.
        :param pos_order: dictionary representing the order.
        :type pos_order: dict.
        :param order: Order object the payment lines should belong to.
        :type order: pos.order
        :param pos_session: PoS session the order was created in.
        :type pos_session: pos.session
        :param draft: Indicate that the pos_order is not validated yet.
        :type draft: bool.
        """
        prec_acc = order.currency_id.decimal_places

        order._clean_payment_lines()
        for payments in pos_order['statement_ids']:
            order.add_payment(self._payment_fields(order, payments[2]))

        order.amount_paid = sum(order.payment_ids.mapped('amount'))

        if not draft and not float_is_zero(pos_order['amount_return'], prec_acc):
            cash_payment_method = pos_session.payment_method_ids.filtered('is_cash_count')[:1]
            if not cash_payment_method:
                raise UserError(_("No cash statement found for this session. Unable to record returned cash."))
            return_payment_vals = {
                'name': _('return'),
                'pos_order_id': order.id,
                'amount': -pos_order['amount_return'],
                'payment_date': fields.Datetime.now(),
                'payment_method_id': cash_payment_method.id,
                'is_change': True,
            }
            # add change value by overriding existing methods
            if pos_order['converted_currency_change'] and pos_order['converted_currency_symbol']:
                currency_id = self.env['res.currency'].search(
                    [('symbol', '=', pos_order['converted_currency_symbol'])])
                return_payment_vals.update({
                    'currency_amount': - pos_order['converted_currency_change'],
                    'payment_currency': currency_id.name,
                })
            order.add_payment(return_payment_vals)
