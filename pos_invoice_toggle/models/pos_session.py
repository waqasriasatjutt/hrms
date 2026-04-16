from odoo import models
import logging

_logger = logging.getLogger(__name__)

class PosSession(models.Model):
    _inherit = "pos.session"

    def _get_pos_ui_pos_config(self, params):
        config_data = super()._get_pos_ui_pos_config(params)

        config_data["hide_pos_invoice_button"] = self.config_id.hide_pos_invoice_button

        # _logger.warning("🔍 [CONFIG DATA] Sent to POS: %s", config_data)
        return config_data
