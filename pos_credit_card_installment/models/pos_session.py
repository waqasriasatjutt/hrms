from odoo import api, fields, models, tools, _
import logging

_logger = logging.getLogger(__name__)


class PosSession(models.Model):
    _inherit = 'pos.session'

    @api.model
    def _load_pos_data_models(self, config_id):
        models = super()._load_pos_data_models(config_id) + ['account.card', 'account.card.installment']
        _logger.info(f"POS Data Models for config {config_id}: {models}")
        return models