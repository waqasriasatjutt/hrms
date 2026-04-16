# -*- coding: utf-8 -*-

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    auto_invoice_check = fields.Boolean(string='Auto-check Invoice', default=False)
    disable_auto_invoice_download = fields.Boolean(string='Disable Invoice Download', default=False)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_auto_invoice_check = fields.Boolean(related='pos_config_id.auto_invoice_check', readonly=False, )
    pos_disable_auto_invoice_download = fields.Boolean(related='pos_config_id.disable_auto_invoice_download',
                                                       readonly=False, )
