# Powered by Sensible Consulting Services
# -*- coding: utf-8 -*-
# © 2025 Sensible Consulting Services (<https://sensiblecs.com/>)
from odoo import fields, models


class SblPosOrder(models.Model):
    _inherit = 'pos.order'

    def sbl_open_pos(self):
        return self.env.user.sbl_pos_config_id.open_ui()