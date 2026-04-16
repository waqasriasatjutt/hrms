from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    allow_remove_orderline = fields.Boolean(string="POS Orderline Remove")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    allow_remove_orderline = fields.Boolean(string="POS Orderline Remove",
                                            related='pos_config_id.allow_remove_orderline',
                                            readonly=False)
