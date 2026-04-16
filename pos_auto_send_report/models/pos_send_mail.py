from odoo import models, api
from datetime import datetime
import io
import xlsxwriter
import base64

class PosReportEmail(models.Model):
    _name = 'pos.report.email'
    _description = 'POS Daily XLSX Report Email Automation'

    @api.model
    def send_daily_pos_report_email(self):
        """Send daily POS sales reports as XLSX attachments to configured recipients"""
        today = datetime.utcnow().date()
        now = datetime.utcnow()
        start_datetime = datetime.combine(today, datetime.min.time())
        end_datetime = datetime.combine(today, datetime.max.time())

        pos_configs = self.env['pos.config'].sudo().search([('send_auto_email', '!=', False)])

        for config in pos_configs:
            email_list = [e.strip() for e in config.send_auto_email.replace(';', ',').replace(' ', ',').split(',') if e.strip()]
            if not email_list:
                continue

            orders = self.env['pos.order'].sudo().search([
                ('config_id', '=', config.id),
                ('date_order', '>=', start_datetime),
                ('date_order', '<=', end_datetime),
                ('state', 'in', ['paid', 'done', 'invoiced']),
            ])
            if not orders:
                continue

            company = config.company_id
            company_name = company.name
            currency = config.currency_id or company.currency_id
            total_amount = sum(order.amount_total for order in orders)
            total_orders = len(orders)
            cashier_list = list(set(orders.mapped('user_id.name')))

            # -------------------------------
            # 1️⃣ POS DAILY REPORT XLSX
            # -------------------------------
            output1 = io.BytesIO()
            workbook1 = xlsxwriter.Workbook(output1, {'in_memory': True})
            bold = workbook1.add_format({'bold': True})
            money = workbook1.add_format({'num_format': '#,##0.000'})
            sheet = workbook1.add_worksheet('POS Daily Report')

            row = 0
            sheet.write(row, 0, company_name, bold)
            row += 1
            sheet.write(row, 0, 'POS Daily Report', bold)
            row += 2
            sheet.write(row, 0, 'Date', bold)
            sheet.write(row, 1, today.strftime('%d-%b-%Y'))
            row += 1
            sheet.write(row, 0, 'POS', bold)
            sheet.write(row, 1, config.name)
            row += 1
            sheet.write(row, 0, 'Cashiers', bold)
            sheet.write(row, 1, ', '.join(cashier_list))
            row += 1
            sheet.write(row, 0, 'Total Orders', bold)
            sheet.write(row, 1, total_orders)
            row += 1
            sheet.write(row, 0, 'Total Sales', bold)
            sheet.write_number(row, 1, total_amount, money)
            row += 2

            # Payment Summary
            sheet.write(row, 0, 'Payment Method Summary', bold)
            row += 1
            sheet.write(row, 0, 'Method', bold)
            sheet.write(row, 1, 'Amount', bold)
            row += 1

            payment_summary = {}
            for order in orders:
                for payment in order.payment_ids:
                    method = payment.payment_method_id.name
                    payment_summary[method] = payment_summary.get(method, 0.0) + payment.amount

            for method, amount in payment_summary.items():
                sheet.write(row, 0, method)
                sheet.write_number(row, 1, amount, money)
                row += 1

            workbook1.close()
            output1.seek(0)
            xlsx_file1 = base64.b64encode(output1.read())

            # -------------------------------
            # 2️⃣ ITEM CONSUMPTION REPORT XLSX
            # -------------------------------
            output2 = io.BytesIO()
            workbook2 = xlsxwriter.Workbook(output2, {'in_memory': True})
            bold2 = workbook2.add_format({'bold': True})
            category_format = workbook2.add_format({'bold': True, 'bg_color': '#D9D9D9'})
            money2 = workbook2.add_format({'num_format': '#,##0.000'})
            sheet2 = workbook2.add_worksheet('Item Consumption')

            row2 = 0
            sheet2.write(row2, 0, company_name, bold2)
            row2 += 1
            sheet2.write(row2, 0, 'Item Consumption Report', bold2)
            row2 += 1
            sheet2.write(row2, 0, f'Reporting For : {today.strftime("%d-%b-%Y")}')
            row2 += 2
            sheet2.write(row2, 0, 'Particulars', bold2)
            sheet2.write(row2, 1, 'Qty', bold2)
            sheet2.write(row2, 2, 'Amount', bold2)
            row2 += 1

            item_summary = {}
            for order in orders:
                for line in order.lines:
                    categ = line.product_id.categ_id.name or 'Uncategorized'
                    prod = line.product_id.display_name
                    qty = line.qty
                    amt = line.price_subtotal
                    if categ not in item_summary:
                        item_summary[categ] = {}
                    if prod not in item_summary[categ]:
                        item_summary[categ][prod] = {'qty': 0, 'amt': 0}
                    item_summary[categ][prod]['qty'] += qty
                    item_summary[categ][prod]['amt'] += amt

            for categ, products in item_summary.items():
                sheet2.write(row2, 0, categ, category_format)
                row2 += 1
                for p, vals in products.items():
                    sheet2.write(row2, 0, p)
                    sheet2.write_number(row2, 1, vals['qty'], money2)
                    sheet2.write_number(row2, 2, vals['amt'], money2)
                    row2 += 1
                row2 += 1

            workbook2.close()
            output2.seek(0)
            xlsx_file2 = base64.b64encode(output2.read())

            # -------------------------------
            # 3️⃣ SALES DETAILS REPORT XLSX
            # -------------------------------
            output3 = io.BytesIO()
            workbook3 = xlsxwriter.Workbook(output3, {'in_memory': True})
            bold3 = workbook3.add_format({'bold': True})
            money3 = workbook3.add_format({'num_format': '#,##0.000'})
            sheet3 = workbook3.add_worksheet('Sales Details')

            row3 = 0
            sheet3.write(row3, 0, company_name, bold3)
            row3 += 1
            sheet3.write(row3, 0, 'Sales Details Report', bold3)
            row3 += 1
            sheet3.write(row3, 0, f'Date: {today.strftime("%d-%b-%Y")}')
            row3 += 2

            headers = ['Category', 'Product', 'Qty Sold', 'Subtotal', 'Discount']
            for col, header in enumerate(headers):
                sheet3.write(row3, col, header, bold3)
            row3 += 1

            sales_summary = {}
            for order in orders:
                for line in order.lines:
                    category = line.product_id.categ_id.name or 'Uncategorized'
                    product = line.product_id.display_name
                    qty = line.qty
                    subtotal = line.price_subtotal
                    discount = line.discount if hasattr(line, 'discount') else 0

                    if category not in sales_summary:
                        sales_summary[category] = {}
                    if product not in sales_summary[category]:
                        sales_summary[category][product] = {'qty': 0, 'subtotal': 0.0, 'discount': 0.0}

                    sales_summary[category][product]['qty'] += qty
                    sales_summary[category][product]['subtotal'] += subtotal
                    sales_summary[category][product]['discount'] += discount

            for category, products in sales_summary.items():
                sheet3.write(row3, 0, category, bold3)
                row3 += 1
                for product, vals in products.items():
                    sheet3.write(row3, 1, product)
                    sheet3.write_number(row3, 2, vals['qty'], money3)
                    sheet3.write_number(row3, 3, vals['subtotal'], money3)
                    sheet3.write_number(row3, 4, vals['discount'], money3)
                    row3 += 1
                row3 += 1

            workbook3.close()
            output3.seek(0)
            xlsx_file3 = base64.b64encode(output3.read())

            # -------------------------------
            # 4️⃣ MANAGER'S REPORT XLSX
            # -------------------------------
            output4 = io.BytesIO()
            workbook4 = xlsxwriter.Workbook(output4, {'in_memory': True})
            bold4 = workbook4.add_format({'bold': True})
            money4 = workbook4.add_format({'num_format': '#,##0.000'})
            sheet4 = workbook4.add_worksheet("Manager's Report")

            row4 = 0
            sheet4.write(row4, 0, company_name, bold4)
            row4 += 1
            sheet4.write(row4, 0, "Report : Manager's Report", bold4)
            row4 += 1
            sheet4.write(row4, 0, f"Reporting For : {today.strftime('%a %d-%b-%Y')} To {today.strftime('%a %d-%b-%Y')}")
            row4 += 1
            sheet4.write(row4, 0, f"Printed On : {now.strftime('%a %d-%b-%Y %I:%M:%S %p')}")
            row4 += 2

            sheet4.write(row4, 0, '-' * 120)
            row4 += 2
            sheet4.write(row4, 0, 'SALE BY MODE OF SETTLEMENT', bold4)
            row4 += 1
            sheet4.write(row4, 0, '-' * 26)
            row4 += 1
            sheet4.write(row4, 0, 'Settlement', bold4)
            sheet4.write(row4, 1, 'Amount', bold4)
            row4 += 1
            sheet4.write(row4, 0, '-' * 120)
            row4 += 1

            for method, amount in payment_summary.items():
                sheet4.write(row4, 0, method)
                sheet4.write_number(row4, 1, amount, money4)
                row4 += 1

            sheet4.write(row4, 0, '-' * 120)
            row4 += 1
            sheet4.write(row4, 0, 'Total', bold4)
            sheet4.write_number(row4, 1, total_amount, money4)
            row4 += 2
            note_text = ("NOTE : In case of Part Settlement the bill will be counted for each type of settlement.\n"
                         "Hence the No Of Bills count shown in this section can be different than the actual No Of Bills printed.")
            sheet4.write(row4, 0, note_text)

            workbook4.close()
            output4.seek(0)
            xlsx_file4 = base64.b64encode(output4.read())

            # -------------------------------
            # SEND EMAIL
            # -------------------------------
            mail_vals = {
                'subject': f'POS Daily Reports - {today.strftime("%d-%b-%Y")} ({config.name})',
                'body_html': f'''
                    <p>Hello,</p>
                    <p>Attached are your POS reports for <b>{today.strftime("%d-%b-%Y")}</b>.</p>
                    <ul>
                        <li>POS Daily Report</li>
                        <li>Item Consumption Report</li>
                        <li>Sales Details Report</li>
                        <li>Manager's Report</li>
                    </ul>
                    <p>Regards,<br/>Odoo POS System</p>
                ''',
                'attachment_ids': [
                    (0, 0, {
                        'name': f'POS_Daily_Report_{today.strftime("%d-%b-%Y")}.xlsx',
                        'type': 'binary',
                        'datas': xlsx_file1,
                        'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    }),
                    (0, 0, {
                        'name': f'Item_Consumption_{today.strftime("%d-%b-%Y")}.xlsx',
                        'type': 'binary',
                        'datas': xlsx_file2,
                        'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    }),
                    (0, 0, {
                        'name': f'Sales_Details_Report_{today.strftime("%d-%b-%Y")}.xlsx',
                        'type': 'binary',
                        'datas': xlsx_file3,
                        'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    }),
                    (0, 0, {
                        'name': f'Manager_Report_{today.strftime("%d-%b-%Y")}.xlsx',
                        'type': 'binary',
                        'datas': xlsx_file4,
                        'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    }),
                ]
            }

            for email in email_list:
                mail = self.env['mail.mail'].sudo().create({
                    **mail_vals,
                    'email_to': email,
                })
                mail.send()
