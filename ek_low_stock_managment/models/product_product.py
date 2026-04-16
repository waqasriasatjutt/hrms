# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_low_stock_alert = fields.Boolean(
        string="Low Stock Alert",
        help='This field determines the minimum stock quantity at which a low '
             'stock alert will be triggered.When the product quantity falls '
             'below this value, the background color for the product will be '
             'changed based on the alert state.',
    )
    min_low_stock_alert = fields.Integer(
        string='Alert Quantity',
        help='Change the background color for the product based'
             'on the Alert Quant.')


    @api.model
    def _load_pos_data_fields(self, config_id):

        fields = super(ProductProduct, self)._load_pos_data_fields(config_id)
        
        fields.append('qty_available')
        fields.append('min_low_stock_alert')

        return fields

    # def nt_get_product_info_pos(self, location, product):
    #     # Warehouses
    #     stock_quantity = self.env['stock.quant'].sudo().search([
    #         ('product_id', '=',product ),
    #         ('location_id', '=', location)
    #         ])

    #     if stock_quantity:
    #         return stock_quantity.quantity
    #     else:
    #         return stock_quantity

    @api.model
    def nt_get_product_info_pos(self, location, product_ids):
        quantities = {}
        stock_quantities = self.env['stock.quant'].sudo().read_group(
            [('product_id', 'in', product_ids), ('location_id', '=', location)],
            ['product_id', 'quantity'],
            ['product_id']
        )

        # Format result as a dictionary with product_id as key and quantity as value
        for quant in stock_quantities:
            quantities[quant['product_id'][0]] = quant['quantity']

        # Return quantity 0 for products with no stock_quant records
        for product_id in product_ids:
            if product_id not in quantities:
                quantities[product_id] = 0.0

        return quantities
