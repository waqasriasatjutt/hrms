from odoo import models, fields

class SaleItemSummaryWizard(models.TransientModel):
    _name = "sale.item.summary.wizard"
    _description = "Sales Item Summary Wizard"

    date_from = fields.Date(string="From Date")
    date_to = fields.Date(string="To Date")
    # report_format = fields.Selection([
    #     ("pdf", "PDF"),
    #     ("xlsx", "Excel"),
    # ], string="Report Format", default="pdf")

    def action_print_report(self):
        domain = []
        if self.date_from:
            domain.append(("date_order", ">=", self.date_from))
        if self.date_to:
            domain.append(("date_order", "<=", self.date_to))

        orders = self.env["pos.order"].search(domain)

        # if self.report_format == "xlsx":
        return self.env.ref("sale_item_summary_report.action_report_sale_item_summary_xlsx").report_action(orders)
        # else:
        #     return self.env.ref("sale_item_summary_report.action_report_sale_item_summary_pdf").report_action(orders)
