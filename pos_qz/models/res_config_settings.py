# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_config_id = fields.Many2one(
        'pos.config',
        string='POS Configuration',
        required=True,
        default=lambda self: self.env['pos.config'].search([], limit=1)
    )


    # qz_kitchen_printer = fields.Char(
    #     string="Kitchen Printer",
    #     related="pos_config_id.qz_kitchen_printer",
    #     readonly=False
    # )
    #
    # qz_report_printer = fields.Char(
    #     string="Report Printer",
    #     related="pos_config_id.qz_report_printer",
    #     readonly=False
    # )
    #
    # qz_receipt_printer = fields.Char(
    #     string="Receipt Printer",
    #     related="pos_config_id.qz_receipt_printer",
    #     readonly=False
    # )


    central_printer_server_ip = fields.Char(
        string="Central Printer Server IP Address",
        related="pos_config_id.central_printer_server_ip",
        readonly=False)

    qz_kitchen_printer_ids = fields.Many2many(
        'qz.printer',
        string="Kitchen Printers",
        related="pos_config_id.qz_kitchen_printer_ids",
        readonly=False
    )

    qz_report_printer_id = fields.Many2one(
        'qz.printer',
        string="Report Printer",
        related="pos_config_id.qz_report_printer_id",
        readonly=False
    )

    qz_receipt_printer_id = fields.Many2one(
        'qz.printer',
        string="Receipt Printer",
        related="pos_config_id.qz_receipt_printer_id",
        readonly=False
    )

    @api.model
    def _load_pos_data_fields(self, config_id):
        fields = super()._load_pos_data_fields(config_id)
        fields += [
            'qz_receipt_printer_id',
            'qz_report_printer_id',
            'qz_kitchen_printer_ids',
        ]
        return fields