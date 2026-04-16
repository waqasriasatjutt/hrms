# Powered by Sensible Consulting Services
# -*- coding: utf-8 -*-
# © 2025 Sensible Consulting Services (<https://sensiblecs.com/>)
from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        info = super().session_info()
        user = self.env.user
        if user.sbl_allow_direct_login and user.sbl_pos_config_id:
            info["home_action_id"] = self.env["ir.actions.server"]._for_xml_id("sensible_pos_direct_login.sbl_pos_login")
        return info