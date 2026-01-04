# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class PosConfig(models.Model):
    _inherit = 'pos.config'

    qz_kitchen_printer_ids = fields.Many2many(
        'qz.printer',
        'pos_config_kitchen_printer_rel',  # relation table
        'pos_config_id',  # this model's FK
        'printer_id',  # qz.printer's FK
        string='Kitchen Printers',
        help='Select one or multiple printers from QZ printers for Kitchen printing.'
    )

    qz_report_printer_id = fields.Many2one(
        'qz.printer',
        string='Report Printer',
        help='Select a printer from QZ printers for POS Reports.'
    )

    qz_receipt_printer_id = fields.Many2one(
        'qz.printer',
        string='Receipt Printer',
        help='Select a printer from QZ printers for Customer Receipts.'
    )


    # @api.model
    # def _load_pos_data_fields(self, config_id):
    #     fields = super()._load_pos_data_fields(config_id)
    #     # Add your custom QZ fields
    #     fields += ['qz_receipt_printer_id', 'qz_report_printer_id', 'qz_kitchen_printer_ids']
    #     return fields
