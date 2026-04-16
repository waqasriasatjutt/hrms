# Powered by Sensible Consulting Services
# -*- coding: utf-8 -*-
# © 2025 Sensible Consulting Services (<https://sensiblecs.com/>)
from odoo import fields, models
from odoo.http import request


class SblPosSession(models.Model):
    _inherit = 'pos.session'

    def close_session_from_ui(self, bank_payment_method_diff_pairs=None):
        res = super().close_session_from_ui(bank_payment_method_diff_pairs=bank_payment_method_diff_pairs)
        if self.user_id.sbl_allow_direct_login:
            request.session.logout(keep_db=True)
        return res