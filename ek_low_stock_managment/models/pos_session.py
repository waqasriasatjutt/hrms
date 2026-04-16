# -*- coding: utf-8 -*-
from odoo import models


class PosSession(models.Model):
    """Inherited pos session for loading quantity fields from product"""
    _inherit = 'pos.session'

    # def _load_pos_data_models(self, config_id):
        
    #     result = super()._load_pos_data_models(config_id)
    #     # result['search_params']['fields'].append('qty_available')
    #     # result['search_params']['fields'].append('min_low_stock_alert')
    #     result.append('qty_available')
    #     result.append('min_low_stock_alert')
    #     return result
