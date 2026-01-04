# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PosPrinter(models.Model):
    _name = 'qz.printer'
    _description = 'POS Printer'
    _rec_name = 'name'
    _order = 'name'

    name = fields.Char(required=True)
    description = fields.Text()
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )

    # --------------------------------------------------
    # POS LOADER METHODS (Odoo 17 compliant)
    # --------------------------------------------------

    @api.model
    def _load_pos_data_fields(self, config_id):
        return ['id', 'name']

    @api.model
    def _load_pos_data(self, response):
        config_id = response['pos.config']['data'][0]['id']
        config = self.env['pos.config'].browse(config_id)

        records = self.search_read(
            [('company_id', '=', config.company_id.id)],
            self._load_pos_data_fields(config_id),
        )

        return {
            'data': records or [],   # NEVER None
            'fields': self._load_pos_data_fields(config_id),
        }
