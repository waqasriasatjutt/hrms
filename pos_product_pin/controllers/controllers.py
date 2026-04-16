from odoo import http
from odoo.http import request

class POSPinProductController(http.Controller):

    @http.route('/pos/pin_product', type='json', auth='user')
    def pin_product(self, template_id, new_value):

        if not template_id:
            return {'error': 'Missing product template ID'}

        product_template = request.env['product.template'].browse(int(template_id))
        if not product_template.exists():
            return {'error': 'Product template not found'}

        product_template.write({'is_pin_product': new_value})
        return {'success': True}