from odoo import models, api
# Import logger
import logging

_logger = logging.getLogger(__name__)

class PosSession(models.Model):

    _inherit = 'pos.session'

    # @api.model
    # def _load_pos_data_models(self, config_id):
        # data = super()._load_pos_data_models(config_id)
        # data += ['pos.pinvandaag.payment.method']
        # return data
    