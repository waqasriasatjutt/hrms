from odoo import models, fields


class ItemDetailWizard(models.TransientModel):
    _name = 'item.detail.wizard'
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)

    def action_print_pdf(self):
        return self.env.ref('item_detail_report.action_item_detail_pdf').report_action(self, data={
            'date_from': self.date_from, 'date_to': self.date_to})

    def action_print_excel(self):
        return self.env.ref('item_detail_report.action_item_detail_xlsx').report_action(self, data={
            'date_from': self.date_from, 'date_to': self.date_to})
