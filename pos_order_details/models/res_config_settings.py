from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # Added a new field. #T6479
    pos_order_detail_button = fields.Boolean(
        related="pos_config_id.order_detail_button", readonly=False
    )
