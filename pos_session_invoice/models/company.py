from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    pos_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Default Customer (POS)",
        help="Default customer to be used in Point of Sale if not specified for a session/order.",
    )
