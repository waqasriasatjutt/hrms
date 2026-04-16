# -*- coding: utf-8 -*-
from odoo import models, api, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    vendor_product_name = fields.Char('Vendor Product Name', compute="_compute_vendor_info", store=True)
    vendor_product_code = fields.Char('Vendor Product Code', compute="_compute_vendor_info", store=True)

    @api.depends('seller_ids', 'seller_ids.product_name', 'seller_ids.product_code')
    def _compute_vendor_info(self):
        for rec in self:
            if rec.seller_ids:
                rec.vendor_product_name = rec.seller_ids[0].product_name
                rec.vendor_product_code = rec.seller_ids[0].product_code
            else:
                rec.vendor_product_name = False
                rec.vendor_product_code = False
