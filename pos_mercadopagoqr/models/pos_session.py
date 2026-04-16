# -*- coding: utf-8 -*-
# Copyright (C) 2024 Axcelere.
# Licensed under the GPL-3.0 License or later.

from odoo import models


class PosSession(models.Model):
    _inherit = 'pos.session'

    # def _loader_params_pos_payment_method(self):
    #     result = super()._loader_params_pos_payment_method()
    #     result['search_params']['fields'].append('pos_mp_config_id')
    #     return result

    def _loader_params_pos_order(self):
        return {
            'search_params': {
                'fields': [
                    'mpqr_payment_token',
                ],
            }
        }

    # def _get_pos_ui_pos_order_by_params(self, custom_search_params):
    #     """
    #     :param custom_search_params: a dictionary containing params of a search_read()
    #     """
    #     params = self._loader_params_pos_payment_method()
    #     # custom_search_params will take priority
    #     params['search_params'] = {**params['search_params'], **custom_search_params}
    #     order = self.env['pos.order'].search_read(**params['search_params'])
    #     return order
