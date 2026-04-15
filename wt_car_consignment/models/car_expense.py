from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CarExpense(models.Model):
    _name = 'car.expense'
    _description = 'Car Expense'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(string="Expense Description", required=True, tracking=True)
    car_id = fields.Many2one('product.template', string="Car", tracking=True)
    partner_id = fields.Many2one('res.partner', string="Vendor / Supplier", required=True)
    date = fields.Date(string="Date", default=fields.Date.context_today)
    amount = fields.Monetary(string="Amount", currency_field='currency_id', tracking=True, required=True)
    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        default=lambda self: self.env.company.currency_id
    )
    notes = fields.Text(string="Notes")
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env.company
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('cancel', 'Cancelled'),
    ], string="Status", default='draft', tracking=True)
    bill_id = fields.Many2one('account.move', string="Vendor Bill", readonly=True, copy=False)

    # ------------------------------
    # ACTIONS
    # ------------------------------
    def action_approve(self):
        """Create and post a vendor bill when approving."""
        for expense in self:
            if expense.state != 'draft':
                raise UserError(_("Only draft expenses can be approved."))
            if expense.bill_id:
                raise UserError(_("A Vendor Bill is already linked to this expense."))

            # 🔎 Find purchase journal
            journal = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)
            if not journal:
                raise UserError(_("No Purchase Journal found. Please create one before approving."))

            # 🧾 Prepare bill values
            bill_vals = {
                'move_type': 'in_invoice',
                'partner_id': expense.partner_id.id,
                'invoice_date': expense.date,
                'journal_id': journal.id,
                'car_id': expense.car_id.id if expense.car_id else False,
                'invoice_line_ids': [(0, 0, {
                    'name': expense.name or "Car Expense",
                    'quantity': 1,
                    'price_unit': expense.amount,
                    'analytic_distribution': {},  # optional
                })],
                'invoice_origin': f"Car Expense #{expense.id}",
                'ref': expense.name,
            }

            # 🧾 Create & Post bill
            bill = self.env['account.move'].create(bill_vals)
            bill.action_post()

            # 🔗 Link back to expense
            expense.write({
                'bill_id': bill.id,
                'state': 'approved'
            })

            # 📨 Log message
            expense.message_post(
                body=_("Vendor Bill <a href='#' data-oe-model='account.move' data-oe-id='%d'>%s</a> has been created and posted.")
                % (bill.id, bill.name)
            )

        return True

    def action_cancel(self):
        for expense in self:
            if expense.state == 'approved' and expense.bill_id and expense.bill_id.state == 'posted':
                raise UserError(_("You cannot cancel an expense linked to a posted Vendor Bill. Please cancel the bill first."))
            expense.write({'state': 'cancel'})
        return True

    def action_reset_to_draft(self):
        for expense in self:
            if expense.bill_id and expense.bill_id.state == 'posted':
                raise UserError(_("You cannot reset to draft while the bill is posted. Please cancel the bill first."))
            expense.write({'state': 'draft'})
        return True
