from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CarSaleInvoiceWizard(models.TransientModel):
    _name = 'car.sale.invoice.wizard'
    _description = 'Car Sale Invoice Options'

    car_id = fields.Many2one('product.template', required=True)

    create_commission_invoice = fields.Boolean(
        string="Create Commission Invoice",
        default=True
    )
    create_sale_invoice = fields.Boolean(
        string="Create Sale Price Invoice",
        default=False
    )

    def action_confirm(self):
        self.ensure_one()
        car = self.car_id

        if not (self.create_commission_invoice or self.create_sale_invoice):
            raise UserError(_("Please select at least one invoice type."))

        if not car.purchaser_id:
            raise UserError(_("Please select a Purchaser first."))

        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        if not journal:
            raise UserError(_("No Sales Journal found."))

        invoices = []

        # 🔹 Commission Invoice
        if self.create_commission_invoice:
            if car.commission_amount <= 0:
                raise UserError(_("Commission amount must be greater than zero."))

            inv = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': car.purchaser_id.id,
                'journal_id': journal.id,
                'invoice_date': fields.Date.today(),
                'car_id': car.id,
                'invoice_line_ids': [(0, 0, {
                    'name': f'Commission for {car.name}',
                    'quantity': 1,
                    'price_unit': car.commission_amount,
                })],
            })
            invoices.append(inv)

        # 🔹 Sale Price Invoice
        if self.create_sale_invoice:
            if car.sale_price <= 0:
                raise UserError(_("Sale price must be greater than zero."))

            inv = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': car.purchaser_id.id,
                'journal_id': journal.id,
                'invoice_date': fields.Date.today(),
                'car_id': car.id,
                'invoice_line_ids': [(0, 0, {
                    'name': f'Sale of {car.name}',
                    'quantity': 1,
                    'price_unit': car.sale_price,
                })],
            })
            invoices.append(inv)

        # 🔒 Mark car as sold
        car.write({
            'state': 'sold',
            'sale_date': fields.Date.today(),
            'is_locked': True,
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Car Sold'),
                'message': _('Invoices created successfully.'),
                'type': 'success',
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window_close'
                }
            }
        }

        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'display_notification',
        #     'params': {
        #         'title': _('Car Sold'),
        #         'message': _('Invoices created successfully.'),
        #         'type': 'success',
        #         'sticky': False,
        #     }
        # }
