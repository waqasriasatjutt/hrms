# Powered by Way4Tech
# -*- coding: utf-8 -*-
# © 2026 Way4Tech (<https://way4tech.com/>)

from odoo import fields, models, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    credit_journal = fields.Boolean('Credit Journal')