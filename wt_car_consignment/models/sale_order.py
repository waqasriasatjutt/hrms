from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    owner_id = fields.Many2one('res.partner', string='Car Owner', related='product_id.owner_id', store=True,
                               readonly=True)
    target_price = fields.Monetary(string='Target Price', related='product_id.target_price', store=True, readonly=True)
    commission_profit = fields.Monetary(string='Commission / Profit', compute='_compute_commission_profit', store=True,
                                        currency_field='currency_id')

    @api.depends('price_unit', 'target_price', 'product_uom_qty')
    def _compute_commission_profit(self):
        for line in self:
            if line.product_id and line.product_id.is_consignment and line.price_unit and line.target_price:
                per_unit = line.price_unit - line.target_price
                line.commission_profit = max(per_unit, 0.0) * (line.product_uom_qty or 1)
            else:
                line.commission_profit = 0.0


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_car_sale = fields.Boolean(string="Car Sale", default=False)

    # def _create_invoices(self, grouped=False, final=False):
    #     invoices = super()._create_invoices(grouped=grouped, final=final)
    #     for inv in invoices:
    #         # adjust invoice lines for consignment products so only commission appears
    #         for inv_line in inv.invoice_line_ids:
    #             sale_lines = inv_line.sale_line_ids
    #             if not sale_lines:
    #                 continue
    #             total_commission = 0.0
    #             is_cons = False
    #             for sl in sale_lines:
    #                 if sl.product_id.is_consignment:
    #                     is_cons = True
    #                     total_commission += sl.commission_profit
    #             if is_cons:
    #                 # set invoice line to commission only (single line approach)
    #                 inv_line.price_unit = total_commission if inv_line.quantity in (0, 1) else (total_commission / inv_line.quantity)
    #                 commission_account = self.env['account.account'].search([('code', '=', '400000')], limit=1)
    #                 if not commission_account:
    #                     commission_account = self.env['account.account'].search([('name', 'ilike', 'commission')], limit=1)
    #                 if commission_account:
    #                     inv_line.account_id = commission_account
    #     return invoices

    # Smart button fields
    full_invoice_id = fields.Many2one('account.move', string="Full Sale Invoice", copy=False)
    commission_invoice_id = fields.Many2one('account.move', string="Commission Invoice", copy=False)
    owner_bill_id = fields.Many2one('account.move', string="Owner Bill", copy=False)

    def action_confirm(self):
        """Confirm the sale, create all related invoices/bills."""
        res = super().action_confirm()

        for order in self:
            if not order.is_car_sale:
                continue

            # === Step 1: Create Full Sale Invoice (not posted) ===
            full_invoice = order._create_full_car_invoice()

            # === Step 2: Create Profit (Commission) Invoice ===
            commission_invoice = order._create_commission_invoice()

            # === Step 3: Create Owner Bill ===
            owner_bill = order._create_owner_bill()

            # Link for smart buttons
            order.write({
                'full_invoice_id': full_invoice.id if full_invoice else False,
                'commission_invoice_id': commission_invoice.id if commission_invoice else False,
                'owner_bill_id': owner_bill.id if owner_bill else False,
            })

            order.message_post(body=_(
                "<b>Car Sale Confirmed</b><br/>"
                "- Full Sale Invoice: <a href=# data-oe-model='account.move' data-oe-id='%d'>%s</a><br/>"
                "- Commission Invoice: <a href=# data-oe-model='account.move' data-oe-id='%d'>%s</a><br/>"
                "- Owner Bill: <a href=# data-oe-model='account.move' data-oe-id='%d'>%s</a>"
            ) % (
                full_invoice.id, full_invoice.name,
                commission_invoice.id, commission_invoice.name,
                owner_bill.id, owner_bill.name
            ))

        return res

    # =====================================================
    # Helper Methods
    # =====================================================

    def _create_full_car_invoice(self):
        """Create normal customer invoice for full sale price (draft only)."""
        self.ensure_one()
        invoices = self._create_invoices(grouped=True, final=False)
        if not invoices:
            raise UserError(_("No invoice created."))
        invoice = invoices[0]
        invoice.write({'state': 'draft'})  # keep unposted
        return invoice

    def _create_commission_invoice(self):
        """Create commission invoice for total profit."""
        self.ensure_one()
        profit_total = sum(self.order_line.mapped('commission_profit'))

        if profit_total <= 0:
            return self.env['account.move']

        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        account = self.env['account.account'].search([('code', '=', '400000')], limit=1)
        if not account:
            account = self.env['account.account'].search([('name', 'ilike', 'commission')], limit=1)
        if not account:
            raise UserError(_("Please configure a 'Commission Income' account."))

        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'invoice_origin': self.name,
            'invoice_line_ids': [(0, 0, {
                'name': f'Commission on {self.name}',
                'account_id': account.id,
                'quantity': 1,
                'price_unit': profit_total,
            })],
            'journal_id': journal.id,
        }
        commission_invoice = self.env['account.move'].create(invoice_vals)
        return commission_invoice

    def _create_owner_bill(self):
        """Create a vendor bill for each car owner based on target_price per car line."""
        self.ensure_one()
        owner_lines = self.order_line.filtered(lambda l: l.owner_id and l.target_price > 0)

        if not owner_lines:
            return self.env['account.move']

        journal = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)
        bills = self.env['account.move']

        for owner in owner_lines.mapped('owner_id'):
            lines = owner_lines.filtered(lambda l: l.owner_id == owner)

            bill_line_vals = []
            for line in lines:
                account = (
                        line.product_id.property_account_expense_id
                        or line.product_id.categ_id.property_account_expense_categ_id
                        or owner.property_account_payable_id
                )
                bill_line_vals.append((0, 0, {
                    'name': f'Payment for {line.product_id.display_name or "Car"} ({line.name})',
                    'account_id': account.id,
                    'quantity': 1,
                    'price_unit': line.target_price,
                    'product_id': line.product_id.id,
                }))

            bill_vals = {
                'move_type': 'in_invoice',
                'partner_id': owner.id,
                'invoice_origin': self.name,
                'invoice_line_ids': bill_line_vals,
                'journal_id': journal.id,
                'invoice_date': fields.Date.context_today(self),
            }

            bill = self.env['account.move'].create(bill_vals)
            bills |= bill

        return bills[0] if bills else self.env['account.move']

    # def _create_owner_bill(self):
    #     """Create a vendor bill per owner, using each car's target_price."""
    #     self.ensure_one()
    #     owner_lines = self.order_line.filtered(lambda l: l.owner_id and l.target_price > 0)
    #
    #     if not owner_lines:
    #         return self.env['account.move']
    #
    #     journal = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)
    #     bills = self.env['account.move']
    #
    #     for owner in owner_lines.mapped('owner_id'):
    #         lines = owner_lines.filtered(lambda l: l.owner_id == owner)
    #         total_target = sum(lines.mapped('target_price'))
    #
    #         bill_vals = {
    #             'move_type': 'in_invoice',
    #             'partner_id': owner.id,
    #             'invoice_origin': self.name,
    #             'invoice_line_ids': [(0, 0, {
    #                 'name': f'Payment for {len(lines)} consigned car(s)',
    #                 'account_id': owner.property_account_payable_id.id,
    #                 'quantity': 1,
    #                 'price_unit': total_target,
    #             })],
    #             'journal_id': journal.id,
    #         }
    #         bill = self.env['account.move'].create(bill_vals)
    #         bills |= bill
    #
    #     return bills[0] if bills else self.env['account.move']

    # =====================================================
    # Smart Button Actions
    # =====================================================

    def action_view_full_invoice(self):
        self.ensure_one()
        if not self.full_invoice_id:
            raise UserError(_("No Full Sale Invoice created yet."))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.full_invoice_id.id,
        }

    def action_view_commission_invoice(self):
        self.ensure_one()
        if not self.commission_invoice_id:
            raise UserError(_("No Commission Invoice created yet."))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.commission_invoice_id.id,
        }

    def action_view_owner_bill(self):
        self.ensure_one()
        if not self.owner_bill_id:
            raise UserError(_("No Owner Bill created yet."))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.owner_bill_id.id,
        }