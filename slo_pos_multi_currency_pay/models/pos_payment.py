from odoo import fields, models


class PosPayment(models.Model):
    _inherit = 'pos.payment'

    payment_currency = fields.Char(string='Payment Currency',
                                   help='Currency in POS settings.')
    currency_amount = fields.Float(string='Currency Amount',
                                   help='Currency amount settings.')


    def get_currency_amount(self, **kwargs):
        session_id = kwargs.get('session_id')
        if not session_id:
            return []

        # Fetch all payments for this session
        records = self.search_read(
            [('pos_order_id.session_id', '=', session_id)],
            ['payment_currency', 'currency_amount', 'payment_method_id']
        )

        # Aggregate by (currency, payment_method_id)
        payment_sums = {}
        for rec in records:
            currency = rec['payment_currency']
            method = rec['payment_method_id']  # This is a [id, name] pair from search_read
            amount = rec['currency_amount'] or 0.0

            # Use tuple as key
            key = (currency, method[1] if method else None)  # method[0] = id
            payment_sums[key] = payment_sums.get(key, 0.0) + amount

        # Convert to list of dicts for JSON response
        result = []
        for (currency, method_id), total in payment_sums.items():
            if total <= 0:
                continue
            currency_id = self.env['res.currency'].search([('name', '=', currency)], limit=1,)
            result.append({
                'payment_currency': currency,
                'payment_method_id': method_id,
                'currency_amount': total,
                'payment_currency_id': currency_id.id,
            })

        return result