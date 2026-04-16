from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    pos_logo = fields.Binary(string="POS Logo")
    show_logo_receipt = fields.Boolean(string="Show Logo On Receipt")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_logo = fields.Binary(string="POS Logo", related='pos_config_id.pos_logo',
                                 readonly=False)
    show_logo_receipt = fields.Boolean(string="Show Logo On Receipt", related='pos_config_id.show_logo_receipt',
                                       readonly=False)
