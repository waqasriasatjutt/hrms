from odoo import models

class DailySalesXlsx(models.AbstractModel):
    _name = 'report.daily_sales_report.daily_sales_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        # Create worksheet
        sheet = workbook.add_worksheet('Daily Sales')

        # Formats
        bold = workbook.add_format({'bold': True})

        # Header row
        headers = ['Date', 'Order', 'Customer', 'Total', 'Cash', 'Card', 'Customer Account']
        for col, header in enumerate(headers):
            sheet.write(0, col, header, bold)

        # Set column widths
        sheet.set_column(0, 0, 20)  # Date
        sheet.set_column(1, 1, 20)  # Order
        sheet.set_column(2, 2, 25)  # Customer
        sheet.set_column(3, 5, 15)  # Amount columns
        sheet.set_column(6, 6, 20)  # Amount columns

        # Fetch POS orders
        orders = self.env['pos.order'].search([
            ('date_order', '>=', wizard.date_from),
            ('date_order', '<=', wizard.date_to),
            ('state', 'in', ['paid', 'done', 'invoiced']),
        ])

        row = 1

        for o in orders:
            # Initialize amounts
            cash = card = customer_account = 0.0

            # Loop payments
            for p in o.payment_ids:
                # normalize name
                name = (p.payment_method_id.name or '').strip().lower()

                # classify payments
                if 'cash' in name:
                    cash += p.amount

                elif 'card' in name:
                    card += p.amount

                elif 'customer account' in name:  # ✅ FIXED
                    customer_account += p.amount

            # Write row data
            sheet.write(row, 0, str(o.date_order))
            sheet.write(row, 1, o.name)
            sheet.write(row, 2, o.partner_id.name if o.partner_id else 'Guest')
            sheet.write(row, 3, o.amount_total)
            sheet.write(row, 4, cash)
            sheet.write(row, 5, card)
            sheet.write(row, 6, customer_account)

            row += 1


# from odoo import models
#
# class DailySalesXlsx(models.AbstractModel):
#     _name = 'report.daily_sales_report.daily_sales_xlsx'
#     _inherit = 'report.report_xlsx.abstract'
#
#     def generate_xlsx_report(self, workbook, data, wizard):
#         sheet = workbook.add_worksheet('Daily Sales')
#
#         row = 0
#         sheet.write(row, 0, 'Date')
#         sheet.write(row, 1, 'Order')
#         sheet.write(row, 2, 'Customer')
#         sheet.write(row, 3, 'Total')
#
#         orders = self.env['sale.order'].search([
#             ('date_order', '>=', wizard.date_from),
#             ('date_order', '<=', wizard.date_to),
#             ('state', 'in', ['sale', 'done'])
#         ])
#
#         row += 1
#         for o in orders:
#             sheet.write(row, 0, str(o.date_order))
#             sheet.write(row, 1, o.name)
#             sheet.write(row, 2, o.partner_id.name)
#             sheet.write(row, 3, o.amount_total)
#             row += 1
