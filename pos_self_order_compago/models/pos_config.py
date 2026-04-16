from odoo import fields, models


class PosConfig(models.Model):
    """Inherited pos configuration setting for adding terminal serial number fields to the POS settings"""

    _inherit = 'pos.config'

    def _supported_kiosk_payment_terminal(self):
        supported_terminals = super()._supported_kiosk_payment_terminal()
        supported_terminals.append('compago')

        return supported_terminals
