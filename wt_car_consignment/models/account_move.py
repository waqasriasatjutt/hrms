from odoo import fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    car_id = fields.Many2one(
        'product.template',
        string='Related Car',
        help='Car associated with this commission invoice.'
    )
