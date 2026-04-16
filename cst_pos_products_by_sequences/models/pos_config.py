# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ProductProduct(models.Model):
    _inherit = 'product.template'

    pos_sequence = fields.Integer("PoS Sequence",
                                  help="Add sequence number to display sorted product by Sequence number in PoS")

    @api.model
    def _load_pos_data_fields(self, config_id):
        data = super()._load_pos_data_fields(config_id)
        data += ['pos_sequence']
        return data
