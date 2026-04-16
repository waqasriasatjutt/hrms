import random

from odoo import models, api
from odoo.osv import expression


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    def _payment_request_from_kiosk(self, order):
        if self.use_payment_terminal != 'compago':
            return super()._payment_request_from_kiosk(order)
        else:
            return self.compago_create_payment_intent({
                'amount': order.amount_total,
                'currency': order.currency_id.name,
                'reference': f'{order.config_id.current_session_id.id}_{self.id}_{order.id}_{format(random.randint(0, 36 ** 8), 'x')}',
            })

    @api.model
    def _load_pos_self_data_domain(self, data):
        domain = super()._load_pos_self_data_domain(data)
        if data['pos.config']['data'][0]['self_ordering_mode'] == 'kiosk':
            domain = expression.OR([[('use_payment_terminal', '=', 'compago')], domain])
        return domain
