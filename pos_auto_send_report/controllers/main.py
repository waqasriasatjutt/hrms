from odoo import http
from odoo.http import request
from datetime import datetime
import io
import xlsxwriter
import base64

class PosCombinedReportController(http.Controller):

    @http.route('/send_pos_report_email', type='json', auth='user')
    def send_pos_report_email(self, email, session_id):
        pos_session = request.env['pos.session'].sudo().browse(session_id)
        if not pos_session.exists():
            return {'error': 'Invalid POS session ID'}

        try:
            # ------------------------------------------------
            # Common Setup
            # ------------------------------------------------
            today = datetime.utcnow().date()
            now = datetime.utcnow()
            start_datetime = datetime.combine(today, datetime.min.time())
            end_datetime = datetime.combine(today, datetime.max.time())

            orders = request.env['pos.order'].sudo().search([
                ('session_id', '=', session_id),
                ('date_order', '>=', start_datetime),
                ('date_order', '<=', end_datetime)
            ])

            if not orders:
                return {'error': 'No orders found for today'}

            company_name = pos_session.company_id.name
            currency = pos_session.config_id.currency_id or pos_session.company_id.currency_id
            total_amount = sum(order.amount_total for order in orders)
            total_orders = len(orders)
            cashier = pos_session.user_id.name

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
            sheet.write(row, 0, 'Cashier', bold)
            sheet.write(row, 1, cashier)
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
            # 2️⃣ ITEM CONSUMPTION REPORT XLSX (with POS/0005 style session)
            # -------------------------------
            output2 = io.BytesIO()
            workbook2 = xlsxwriter.Workbook(output2, {'in_memory': True})
            bold2 = workbook2.add_format({'bold': True})
            category_format = workbook2.add_format({'bold': True, 'bg_color': '#D9D9D9'})
            money2 = workbook2.add_format({'num_format': '#,##0.000'})
            italic = workbook2.add_format({'italic': True})
            title_format = workbook2.add_format({'bold': True, 'font_size': 14})
            header_format = workbook2.add_format({'bold': True, 'bg_color': '#E8E8E8', 'border': 1})
            sheet2 = workbook2.add_worksheet('Item Consumption')

            row2 = 0
            sheet2.write(row2, 0, company_name, title_format)
            row2 += 1
            sheet2.write(row2, 0, 'Item Consumption Report', bold2)
            row2 += 1
            sheet2.write(row2, 0, f'Date: {today.strftime("%d-%b-%Y")}')
            row2 += 1
            # ✅ Display POS Session in POS/0005 style
            sheet2.write(row2, 0, f'POS Session: {pos_session.name}', bold2)
            row2 += 1
            sheet2.write(row2, 0, f'Printed On: {now.strftime("%d-%b-%Y %I:%M:%S %p")}')
            row2 += 2

            # Table headers
            sheet2.write(row2, 0, 'Particulars', header_format)
            sheet2.write(row2, 1, 'Sale Qty', header_format)
            sheet2.write(row2, 2, 'Amount', header_format)
            row2 += 1

            # Data calculation
            item_summary = {}
            category_totals = {}
            grand_total = 0.0
            for order in orders:
                for line in order.lines:
                    product = line.product_id
                    category = product.categ_id.name or 'Uncategorized'
                    qty = line.qty
                    amount = line.price_subtotal

                    if category not in item_summary:
                        item_summary[category] = {}
                        category_totals[category] = 0.0
                    if product.display_name not in item_summary[category]:
                        item_summary[category][product.display_name] = {'qty': 0, 'amount': 0.0}

                    item_summary[category][product.display_name]['qty'] += qty
                    item_summary[category][product.display_name]['amount'] += amount
                    category_totals[category] += amount
                    grand_total += amount

            # Write category-wise data
            for category, products in item_summary.items():
                sheet2.write(row2, 0, category, category_format)
                sheet2.write_number(row2, 2, category_totals[category], money2)
                row2 += 1
                for prod_name, vals in products.items():
                    sheet2.write(row2, 0, prod_name)
                    sheet2.write_number(row2, 1, vals['qty'], money2)
                    sheet2.write_number(row2, 2, vals['amount'], money2)
                    row2 += 1
                row2 += 1

            # Totals and footer
            sheet2.write(row2, 0, 'TOTAL', bold2)
            sheet2.write_number(row2, 2, grand_total, money2)
            row2 += 2
            sheet2.write(row2, 0, 'END OF Item Consumption Report', bold2)
            row2 += 2
            sheet2.write(row2, 0, 'NOTE: Amounts indicated are exclusive of discounts and complimentary sales.', italic)

            workbook2.close()
            output2.seek(0)
            xlsx_file2 = base64.b64encode(output2.read())

            # -------------------------------

            # -------------------------------
            # -------------------------------
            # 3️⃣ SALES DETAILS REPORT XLSX (Improved)
            # -------------------------------
            output3 = io.BytesIO()
            workbook3 = xlsxwriter.Workbook(output3, {'in_memory': True})
            bold3 = workbook3.add_format({'bold': True})
            money3 = workbook3.add_format({'num_format': '#,##0.000'})
            italic3 = workbook3.add_format({'italic': True})
            title_format = workbook3.add_format({'bold': True, 'font_size': 14})
            header_format = workbook3.add_format({'bold': True, 'bg_color': '#D9D9D9', 'border': 1})
            sheet3 = workbook3.add_worksheet('Sales Details')

            row3 = 0
            sheet3.write(row3, 0, company_name, title_format)
            row3 += 1
            sheet3.write(row3, 0, 'Sales Details Report', bold3)
            row3 += 1
            sheet3.write(row3, 0, f'Date: {today.strftime("%d-%b-%Y")}')
            row3 += 1
            sheet3.write(row3, 0, f'Session Name: {pos_session.name}', bold3)
            row3 += 2

            # Table Headers
            headers = ['Order', 'Category', 'Product', 'Qty Sold', 'Subtotal', 'Discount']
            for col, header in enumerate(headers):
                sheet3.write(row3, col, header, header_format)
            row3 += 1

            # Collect and display sales details
            sales_summary = []
            for order in orders:
                for line in order.lines:
                    category = line.product_id.categ_id.name or 'Uncategorized'
                    product = line.product_id.display_name
                    qty = line.qty
                    subtotal = line.price_subtotal
                    discount = line.discount if hasattr(line, 'discount') else 0
                    sales_summary.append({
                        'order': order.name,
                        'category': category,
                        'product': product,
                        'qty': qty,
                        'subtotal': subtotal,
                        'discount': discount,
                    })

            # Write each sale line to sheet
            for item in sales_summary:
                sheet3.write(row3, 0, item['order'])
                sheet3.write(row3, 1, item['category'])
                sheet3.write(row3, 2, item['product'])
                sheet3.write_number(row3, 3, item['qty'], money3)
                sheet3.write_number(row3, 4, item['subtotal'], money3)
                sheet3.write_number(row3, 5, item['discount'], money3)
                row3 += 1

            # Add summary totals
            row3 += 2
            sheet3.write(row3, 0, 'TOTAL', bold3)
            sheet3.write_formula(row3, 4, f'=SUM(E5:E{row3})', money3)  # Sum of Subtotal column
            row3 += 2
            sheet3.write(row3, 0, 'Note:', italic3)
            sheet3.write(row3 + 1, 0, 'This report includes all orders and items under the selected POS session.',
                         italic3)

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

            sheet4.write(row4, 0, '-'*120)
            row4 += 2
            sheet4.write(row4, 0, 'SALE BY MODE OF SETTLEMENT', bold4)
            row4 += 1
            sheet4.write(row4, 0, '-'*26)
            row4 += 1
            sheet4.write(row4, 0, 'Settlement', bold4)
            sheet4.write(row4, 1, 'Amount', bold4)
            row4 += 1
            sheet4.write(row4, 0, '-'*120)
            row4 += 1

            for method, amount in payment_summary.items():
                sheet4.write(row4, 0, method)
                sheet4.write_number(row4, 1, amount, money4)
                row4 += 1

            sheet4.write(row4, 0, '-'*120)
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
            # SEND EMAIL WITH ALL FOUR ATTACHMENTS
            # -------------------------------
            mail = request.env['mail.mail'].sudo().create({
                'email_to': email,
                'subject': f'POS, Item Consumption, Sales & Manager Reports - {today.strftime("%d-%b-%Y")}',
                'body_html': f'''
                    <p>Hello,</p>
                    <p>Attached are the reports for {today.strftime("%d-%b-%Y")}:</p>
                    <ul>
                        <li>POS Daily Report</li>
                        <li>Item Consumption Report</li>
                        <li>Sales Details Report</li>
                        <li>Manager's Report</li>
                    </ul>
                    <p>Regards,<br/>Your POS System</p>
                ''',
                'attachment_ids': [

                    (0, 0, {
                        'name': f'POS_Daily_Report_{today.strftime("%d-%b-%Y")}.xlsx',
                        'type': 'binary',
                        'datas': xlsx_file1,
                        'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    }),
                    (0, 0, {
                        'name': f'Item_Consumption_Report_{today.strftime("%d-%b-%Y")}.xlsx',
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
            })
            mail.send()

            return {'status': 'success'}

        except Exception as e:
            return {'error': str(e)}
