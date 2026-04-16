from odoo import models

class ProfitReport(models.AbstractModel):
    _name = 'report.profit_margin_report.template_profit_report'

    def _get_report_values(self, docids, data=None):

        lines = self.env['pos.order.line'].search([
            ('order_id.state', 'in', ['paid', 'done']),
            ('order_id.date_order', '>=', data.get('date_from')),
            ('order_id.date_order', '<=', data.get('date_to')),
        ])


        # Fetch sale order lines

        # lines = self.env['sale.order.line'].search([
        #     ('order_id.state', 'in', ['sale', 'done']),
        #     ('order_id.date_order', '>=', data.get('date_from')),
        #     ('order_id.date_order', '<=', data.get('date_to')),
        # ])

        result = {}

        for line in lines:
            product = line.product_id

            if product not in result:
                result[product] = {
                    'qty': 0,
                    'sale': 0,
                    'cost': 0,
                    'profit': 0,
                }

            # qty = line.product_uom_qty
            qty = line.qty
            sale = line.price_subtotal_incl
            # sale = line.price_subtotal

            # Cost using standard price
            cost = product.standard_price * qty

            profit = sale - cost

            result[product]['qty'] += qty
            result[product]['sale'] += sale
            result[product]['cost'] += cost
            result[product]['profit'] += profit

        # Calculate margin
        for product in result:
            sale = result[product]['sale']
            profit = result[product]['profit']
            result[product]['margin'] = (profit / sale * 100) if sale else 0

        return {
            'products': result
        }
