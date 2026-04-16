from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    allow_auto_invoice_true = fields.Boolean(string='Allow Auto Invoice True',default=True)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    allow_auto_invoice_true = fields.Boolean(string='Allow Auto Invoice True',
                                             related="pos_config_id.allow_auto_invoice_true",
                                             readonly=False)
