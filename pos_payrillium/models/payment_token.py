from odoo import models, fields

class PaymentToken(models.Model):
    _inherit = 'payment.token'

    token_type = fields.Selection([
        ('bank_checking', 'Bank - Checking'),
        ('bank_savings', 'Bank - Savings'),
        ('card_payment', 'Card Payment'),
    ], string="Token Type", readonly=True)
