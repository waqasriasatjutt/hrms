from odoo import models

class ItemDetailXlsx(models.AbstractModel):
    _name = 'report.item_detail_report.item_detail_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        sheet = workbook.add_worksheet('Item Detail')
        bold = workbook.add_format({'bold': True})

        # Header
        headers = ['Product', 'Qty', 'Total']
        for col, header in enumerate(headers):
            sheet.write(0, col, header, bold)

        # Fetch POS order lines
        lines = self.env['pos.order.line'].search([
            ('order_id.state', 'in', ['paid', 'done']),
            ('order_id.date_order', '>=', wizard.date_from),
            ('order_id.date_order', '<=', wizard.date_to),
        ])

        # Aggregate by product
        res = {}
        for line in lines:
            p = line.product_id
            if p not in res:
                res[p] = {'qty': 0, 'subtotal': 0}
            res[p]['qty'] += line.qty
            res[p]['subtotal'] += line.price_subtotal_incl  # POS includes taxes

        # Write data
        sheet.set_column(0, 0, 30)  # Product column wide
        sheet.set_column(1, 1, 10)  # Qty column
        sheet.set_column(2, 2, 15)  # Total column
        row = 1
        for p, v in res.items():
            sheet.write(row, 0, p.name)
            sheet.write(row, 1, v['qty'])
            sheet.write(row, 2, v['subtotal'])
            row += 1

# from odoo import models
#
#
# class ItemDetailXlsx(models.AbstractModel):
#     _name = 'report.item_detail_report.item_detail_xlsx'
#     _inherit = 'report.report_xlsx.abstract'
#
#     def generate_xlsx_report(self, workbook, data, wizard):
#         sheet = workbook.add_worksheet('Item Detail')
#         sheet.write(0, 0, 'Product');
#         sheet.write(0, 1, 'Qty');
#         sheet.write(0, 2, 'Total')
#         lines = self.env['sale.order.line'].search([
#             ('order_id.state', 'in', ['sale', 'done']),
#             ('order_id.date_order', '>=', wizard.date_from),
#             ('order_id.date_order', '<=', wizard.date_to)])
#         res = {}
#         for l in lines:
#             p = l.product_id
#             if p not in res: res[p] = {'qty': 0, 'subtotal': 0}
#             res[p]['qty'] += l.product_uom_qty
#             res[p]['subtotal'] += l.price_subtotal
#         r = 1
#         for p, v in res.items():
#             sheet.write(r, 0, p.name);
#             sheet.write(r, 1, v['qty']);
#             sheet.write(r, 2, v['subtotal']);
#             r += 1
