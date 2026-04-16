from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    # Added a new field. #T6479
    order_detail_button = fields.Boolean(string="View POS Order Details", copy=False)
