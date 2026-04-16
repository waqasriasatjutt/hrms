from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_subtotal_to_qty_pp = fields.Boolean(string="Is subtotal to qty product(?)")

    @api.model
    def _load_pos_data_fields(self, config_id):
        res = super(ProductProduct, self)._load_pos_data_fields(config_id)
        res.append('is_subtotal_to_qty_pp')
        return res