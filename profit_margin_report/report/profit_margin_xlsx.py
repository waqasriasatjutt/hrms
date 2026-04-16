from odoo import models

class ProfitMarginXlsx(models.AbstractModel):
    _name = 'report.profit_margin_report.profit_margin_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        sheet = workbook.add_worksheet('Profit Margin Report')
        bold = workbook.add_format({'bold': True})

        # Header
        headers = ['Product', 'Qty', 'Sales', 'Cost', 'Profit', 'Margin %']
        for col, header in enumerate(headers):
            sheet.write(0, col, header, bold)

        # Fetch POS order lines
        lines = self.env['pos.order.line'].search([
            ('order_id.state', 'in', ['paid', 'done']),
            ('order_id.date_order', '>=', wizard.date_from),
            ('order_id.date_order', '<=', wizard.date_to),
        ])

        # Aggregate data by product
        result = {}
        for line in lines:
            product = line.product_id
            if product not in result:
                result[product] = {'qty': 0, 'sale': 0, 'cost': 0, 'profit': 0}

            qty = line.qty
            sale = line.price_subtotal_incl  # POS includes taxes
            cost = product.standard_price * qty
            profit = sale - cost

            result[product]['qty'] += qty
            result[product]['sale'] += sale
            result[product]['cost'] += cost
            result[product]['profit'] += profit

        # Calculate margin %
        for product in result:
            sale = result[product]['sale']
            profit = result[product]['profit']
            result[product]['margin'] = (profit / sale * 100) if sale else 0

        # Write data
        sheet.set_column(0, 0, 30)  # Product column wide
        sheet.set_column(1, 1, 10)  # Qty column
        sheet.set_column(2, 5, 15)  # Total column
        row = 1
        for product, vals in result.items():
            sheet.write(row, 0, product.name)
            sheet.write(row, 1, vals['qty'])
            sheet.write(row, 2, vals['sale'])
            sheet.write(row, 3, vals['cost'])
            sheet.write(row, 4, vals['profit'])
            sheet.write(row, 5, round(vals['margin'], 2))
            row += 1

# from odoo import models
#
# class ProfitMarginXlsx(models.AbstractModel):
#     _name = 'report.profit_margin_report.profit_margin_xlsx'
#     _inherit = 'report.report_xlsx.abstract'
#
#     def generate_xlsx_report(self, workbook, data, wizard):
#         sheet = workbook.add_worksheet('Profit Margin Report')
#         bold = workbook.add_format({'bold': True})
#
#         # Header
#         headers = ['Product', 'Qty', 'Sales', 'Cost', 'Profit', 'Margin %']
#         for col, header in enumerate(headers):
#             sheet.write(0, col, header, bold)
#
#         # Fetch sale order lines
#         lines = self.env['sale.order.line'].search([
#             ('order_id.state', 'in', ['sale', 'done']),
#             ('order_id.date_order', '>=', wizard.date_from),
#             ('order_id.date_order', '<=', wizard.date_to),
#         ])
#
#         # Aggregate data by product
#         result = {}
#         for line in lines:
#             product = line.product_id
#             if product not in result:
#                 result[product] = {'qty': 0, 'sale': 0, 'cost': 0, 'profit': 0}
#
#             qty = line.product_uom_qty
#             sale = line.price_subtotal
#             cost = product.standard_price * qty
#             profit = sale - cost
#
#             result[product]['qty'] += qty
#             result[product]['sale'] += sale
#             result[product]['cost'] += cost
#             result[product]['profit'] += profit
#
#         for product in result:
#             sale = result[product]['sale']
#             profit = result[product]['profit']
#             result[product]['margin'] = (profit / sale * 100) if sale else 0
#
#         # Write data
#         row = 1
#         for product, vals in result.items():
#             sheet.write(row, 0, product.name)
#             sheet.write(row, 1, vals['qty'])
#             sheet.write(row, 2, vals['sale'])
#             sheet.write(row, 3, vals['cost'])
#             sheet.write(row, 4, vals['profit'])
#             sheet.write(row, 5, round(vals['margin'], 2))
#             row += 1
