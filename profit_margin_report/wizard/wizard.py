from odoo import models, fields


class ProfitWizard(models.TransientModel):
    _name = 'profit.wizard'
    _description = 'Profit Margin Report'

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)

    def action_print_profit(self):
        return self.env.ref('profit_margin_report.action_profit_report').report_action(
            self, data={'date_from': self.date_from, 'date_to': self.date_to}
        )

    def action_print_profit_excel(self):
        return self.env.ref('profit_margin_report.action_profit_report_xlsx').report_action(
            self, data={'date_from': self.date_from, 'date_to': self.date_to}
        )
