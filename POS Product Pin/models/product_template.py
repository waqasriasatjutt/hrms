from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_pin_product = fields.Boolean(string='Is Pin Product',
        help='Indicates whether the product is pinned in the Point of Sale interface.', default=False
    )