from odoo import models, fields

class DailySalesWizard(models.TransientModel):
    _name = 'daily.sales.wizard'
    _description = 'Daily Sales Wizard'

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)

    def action_print_pdf(self):
        # Fetch POS orders in the date range
        orders = self.env['pos.order'].search([
            ('date_order', '>=', self.date_from),
            ('date_order', '<=', self.date_to),
            ('state', 'in', ['paid', 'done', 'invoiced']),
        ])
        data = {'orders': orders.ids}
        return self.env.ref('daily_sales_report.action_daily_sales_report').report_action(self, data=data)

    def action_print_excel(self):
        return self.env.ref('daily_sales_report.action_daily_sales_xlsx').report_action(self)




from odoo import models

class DailySalesReport(models.AbstractModel):
    _name = 'report.daily_sales_report.template_daily_sales'
    _description = 'Daily Sales Report'

    def _get_report_values(self, docids, data=None):
        docs = self.env['daily.sales.wizard'].browse(docids)

        orders = self.env['pos.order'].browse(data.get('orders', [])) if data else []

        order_data = []

        # for o in orders:
        #     cash = card = customer_account = 0.0
        #
        #     for p in o.payment_ids:
        #         name = (p.payment_method_id.name or '').strip().lower()
        #         # for p in o.payment_ids:
        #         print(">>>", p.payment_method_id.name)
        #
        #         if 'cash' in name:
        #             cash += p.amount
        #
        #         elif 'card' in name:
        #             card += p.amount
        #
        #         elif 'Customer Account' in name:
        #             customer_account += p.amount
        #
        #     order_data.append({
        #         'order': o,
        #         'cash': cash,
        #         'card': card,
        #         'customer_account': customer_account,
        #         'credit': credit,
        #     })

        for o in orders:
            cash = card = customer_account = 0.0

            for p in o.payment_ids:
                # normalize name
                name = (p.payment_method_id.name or '').strip().lower()

                # debug (optional)
                print(">>>>>", name)

                # classification
                if 'cash' in name:
                    cash += p.amount

                elif 'card' in name:
                    card += p.amount

                elif 'customer account' in name:  # ✅ FIXED
                    customer_account += p.amount


            order_data.append({
                'order': o,
                'cash': cash,
                'card': card,
                'customer_account': customer_account,
            })

            for p in o.payment_ids:
                print(">>>", p.payment_method_id.name)

        return {
            'doc_ids': docids,
            'doc_model': 'daily.sales.wizard',
            'docs': docs,  # ✅ IMPORTANT (keep this for layout)
            'orders': order_data,  # your custom data
        }




# from odoo import models, fields
#
# class DailySalesWizard(models.TransientModel):
#     _name = 'daily.sales.wizard'
#     _description = 'Daily Sales Wizard'
#
#     date_from = fields.Date(required=True)
#     date_to = fields.Date(required=True)
#
#     def action_print_pdf(self):
#         orders = self.env['sale.order'].search([
#             ('date_order', '>=', self.date_from),
#             ('date_order', '<=', self.date_to),
#             ('state', 'in', ['sale', 'done'])
#         ])
#
#         data = {
#             'orders': orders.ids,
#         }
#
#         return self.env.ref('daily_sales_report.action_daily_sales_report').report_action(self, data=data)
#
#
#     def action_print_excel(self):
#         return self.env.ref('daily_sales_report.action_daily_sales_xlsx').report_action(self)
#
#
#
# from odoo import models
#
# class DailySalesReport(models.AbstractModel):
#     _name = 'report.daily_sales_report.template_daily_sales'
#     _description = 'Daily Sales Report'
#
#     def _get_report_values(self, docids, data=None):
#         docs = self.env['daily.sales.wizard'].browse(docids)
#
#         orders = self.env['sale.order'].browse(data.get('orders', [])) if data else []
#
#         return {
#             'doc_ids': docids,
#             'doc_model': 'daily.sales.wizard',
#             'docs': docs,
#             'orders': orders,
#             'data': data,  # ✅ IMPORTANT
#         }

