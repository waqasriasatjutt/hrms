from odoo import models

class SaleItemSummaryXlsx(models.AbstractModel):
    _name = "report.sale_item_summary_report.sale_item_summary_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Sales Item Summary XLSX"

    def generate_xlsx_report(self, workbook, data, orders):
        sheet = workbook.add_worksheet("Sales Summary")
        bold = workbook.add_format({"bold": True, "bg_color": "#b6d7a8", "border": 1})
        normal = workbook.add_format({"border": 1})
        total_bold = workbook.add_format({"bold": True, "bg_color": "#f9cb9c", "border": 1})

        headers = [
            "S. No", "Item Name", "Barcode", "Date of Sale",
            "Order Reference", "Order Number", "Quantity Sold",
            "Payment Method",
            "Cost Price",
            "Tax Amount",
            "Untaxed Amount","Sale Price",
        ]

        # Header
        for col, header in enumerate(headers):
            sheet.write(0, col, header, bold)

        row = 1
        count = 1

        total_qty = 0.0
        total_cost = 0.0
        total_sale = 0.0
        total_amount = 0.0
        total_tax = 0.0
        total_untaxed = 0.0

        for order in orders:
            for line in order.lines:
                sheet.write(row, 0, count, normal)
                sheet.write(row, 1, line.product_id.display_name or "", normal)
                sheet.write(row, 2, line.product_id.barcode or "", normal)
                sheet.write(row, 3, order.date_order.strftime("%Y-%m-%d") if order.date_order else "", normal)
                sheet.write(row, 4, order.name or "", normal)
                sheet.write(row, 5, order.tracking_number or "", normal)
                sheet.write(row, 6, line.qty or 0.0, normal)
                payment_methods = ", ".join(
                    order.payment_ids.mapped("payment_method_id.name")
                )
                sheet.write(row, 7, payment_methods or "", normal)

                sheet.write(row, 8, line.total_cost or 0.0, normal)
                # sheet.write(row, 8, line.product_id.stan or 0.0, normal)
                sheet.write(row, 9, (line.price_subtotal_incl or 0.0) - (line.price_subtotal or 0.0) , normal)
                sheet.write(row, 10, line.price_unit or 0.0, normal)
                sheet.write(row, 11, line.price_subtotal_incl or 0.0, normal)

                # # Accumulate totals


                tax_amount = (line.price_subtotal_incl or 0.0) - (line.price_subtotal or 0.0)

                total_qty += line.qty or 0.0
                total_cost += line.total_cost or 0.0
                total_tax += tax_amount
                total_untaxed += line.price_subtotal or 0.0
                total_sale += line.price_unit or 0.0
                total_amount += line.price_subtotal_incl or 0.0

                row += 1
                count += 1


        sheet.merge_range(row, 0, row, 5, "TOTAL", total_bold)
        sheet.write(row, 6, total_qty, total_bold)
        sheet.write(row, 7, "", total_bold)
        sheet.write(row, 8, total_cost, total_bold)
        sheet.write(row, 9, total_tax, total_bold)
        sheet.write(row, 10, total_untaxed, total_bold)
        sheet.write(row, 11, total_amount, total_bold)

        # Adjust column widths
        sheet.set_column("A:A", 10)
        sheet.set_column("B:B", 28)
        sheet.set_column("C:L", 18)
