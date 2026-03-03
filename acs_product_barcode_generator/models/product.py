# -*- coding: utf-8 -*-
#Some Reference is taken from exisitng OCA Module

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class res_company(models.Model):
    _inherit = 'res.company'

    barcode_sequence_id = fields.Many2one('ir.sequence', 'Barcode Sequence')
    auto_create_barcode = fields.Boolean('Auto Create Barcode on Product Creation', default=False)


class ir_sequence(models.Model):
    _inherit = 'ir.sequence'
    
    barcode_sequence = fields.Boolean('Barcode Sequence', default=False)


def isodd(x):
    return bool(x % 2)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    barcode_sequence_id = fields.Many2one('ir.sequence', 'Barcode Sequence')

    def generate_barcode(self):
        for template in self:
            for product in template.product_variant_ids:
                product.barcode = product._generate_barcode_value(product)

    @api.onchange('categ_id')
    def onchange_categ_id(self):
        if self.categ_id:
            if self.categ_id.barcode_sequence_id:
                self.barcode_sequence_id = self.categ_id.barcode_sequence_id

    @api.model
    def create(self, values):
        res = super(ProductTemplate, self).create(values)
        if not res.barcode and self.env.user.company_id.auto_create_barcode:
            res.generate_barcode()
        return res


class ProductCategory(models.Model):
    _inherit = 'product.category'

    barcode_sequence_id = fields.Many2one('ir.sequence', 'Barcode Sequence')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def generate_barcode(self):
        for product in self:
            product.barcode = self._generate_barcode_value(product)

    @api.onchange('categ_id')
    def onchange_categ_id(self):
        if self.categ_id:
            if self.categ_id.barcode_sequence_id:
                self.barcode_sequence_id = self.categ_id.barcode_sequence_id

    def _get_barcode_next_code(self, product):
        sequence_obj = self.env['ir.sequence']
        barcode = ''
        if product.barcode_sequence_id:
            barcode = product.barcode_sequence_id.next_by_id()
        elif product.categ_id.barcode_sequence_id:
            barcode = product.categ_id.barcode_sequence_id.next_by_id()
        elif product.company_id and product.company_id.barcode_sequence_id:
            barcode = product.company_id.barcode_sequence_id.next_by_id()
        elif self.env.user.company_id.barcode_sequence_id:
            barcode = self.env.user.company_id.barcode_sequence_id.next_by_id()
        else:
            raise UserError(_('Configure Barcode seq on Product or Product Category or on Compnay.'))
        barcode = (len(barcode[0:6]) == 6 and barcode[0:6] or barcode[0:6].ljust(6,'0')) + barcode[6:].rjust(6,'0')
        if len(barcode) > 12:
           raise ValidationError(_("There next sequence is upper than 12 characters. This can't work."
                  "You will have to redefine the sequence or create a new one"))
        return barcode

    def _get_barcode_key(self, code):
        sum = 0
        for i in range(12):
            if isodd(i):
                sum += 3 * int(code[i])
            else:
                sum += int(code[i])
        key = (10 - sum % 10) % 10
        return str(key) 

    def _generate_barcode_value(self, product):
        barcode = self._get_barcode_next_code(product)
        if not barcode:
            return False
        key = self._get_barcode_key(barcode)
        barcode13 = barcode + key
        return barcode13

    def generate_barcode(self):
        for product in self:
            if product.barcode:
                continue
            barcode13 = product._generate_barcode_value(product)
            if barcode13:
                product.barcode = barcode13

    @api.model
    def create(self, values):
        res = super(ProductProduct, self).create(values)
        if not res.barcode and self.env.user.company_id.auto_create_barcode:
            res.generate_barcode()
        return res
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: