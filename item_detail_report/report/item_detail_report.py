from odoo import models

class ItemDetailReport(models.AbstractModel):
    _name = 'report.item_detail_report.template_item_detail'

    def _get_report_values(self, docids, data=None):
        lines = self.env['pos.order.line'].search([
            ('order_id.state', 'in', ['paid', 'done']),
            ('order_id.date_order', '>=', data.get('date_from')),
            ('order_id.date_order', '<=', data.get('date_to')),
        ])

        result = {}
        for line in lines:
            p = line.product_id
            if p not in result:
                result[p] = {'qty': 0, 'subtotal': 0}
            result[p]['qty'] += line.qty
            result[p]['subtotal'] += line.price_subtotal_incl

        return {'products': result}

# from odoo import models
#
#
# class ItemDetailReport(models.AbstractModel):
#     _name = 'report.item_detail_report.template_item_detail'
#
#     def _get_report_values(self, docids, data=None):
#         lines = self.env['sale.order.line'].search([
#             ('order_id.state', 'in', ['sale', 'done']),
#             ('order_id.date_order', '>=', data.get('date_from')),
#             ('order_id.date_order', '<=', data.get('date_to'))])
#         result = {}
#         for l in lines:
#             p = l.product_id
#             if p not in result: result[p] = {'qty': 0, 'subtotal': 0}
#             result[p]['qty'] += l.product_uom_qty
#             result[p]['subtotal'] += l.price_subtotal
#         return {'products': result}
