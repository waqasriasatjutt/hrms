from odoo import models, fields, api

class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    tax_details = fields.Text("Tax Details1111", help="Stores detailed tax breakdown")
    # taxname = fields.Char(related="Tax Details1111", help="Stores detailed tax breakdown")
    # taxamount = fields.Text("Tax Details1111", help="Stores detailed tax breakdown")
