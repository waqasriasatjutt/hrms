import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

class PosBank(models.TransientModel):
    _name = 'pos.bank'
    _description = 'List of banks for POS'

    @api.model
    def get_bank_code(self):
        selection = [
            ("014", "SCB"),
        ]
        return selection

    