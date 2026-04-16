from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    discount_price = fields.Float(string="Discount Price")
    is_display_discount_price = fields.Boolean(string="Is Display Discount Price",
                                               compute="_compute_is_display_discount_price")

    @api.model
    def _load_pos_data_fields(self, config_id):
        """Returns the fields to be loaded for POS data."""
        result = super()._load_pos_data_fields(config_id)
        result.append('discount_price')
        return result

    @api.onchange('discount_price', 'lst_price')
    def _onchange_discount_price(self):
        if self.discount_price < 0:
            raise ValidationError("Enter Valid Price..")
        if self.discount_price > self.lst_price:
            raise ValidationError("Enter Price Less than Sales_price")

    def _compute_is_display_discount_price(self):
        for rec in self:
            rec.is_display_discount_price = self.env['ir.config_parameter'].sudo().get_param(
                'eg_pos_display_discount_price.display_discount_price')
