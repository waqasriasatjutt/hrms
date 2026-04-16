from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pos_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Default customer",
        check_company=True,
        readonly=False,
        help="Default customer to be used in Point of Sale if not specified.",
        related="company_id.pos_partner_id",
    )
