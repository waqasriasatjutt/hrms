from odoo import _, api, fields, models, tools
from odoo.exceptions import AccessError, UserError, ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    # _inherit = ['product.template', 'mail.thread', 'mail.activity.mixin']

    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        default=lambda self: self.env.company.currency_id,
    )

    # Existing fields
    is_consignment = fields.Boolean(
        string='Consignment Car',
        default=False,
        help='Mark product as consignment car (owned by third party)'
    )
    owner_id = fields.Many2one(
        'res.partner',
        string='Car Owner',
        help='Owner of the car'
    )
    target_price = fields.Monetary(
        string='Target Price',
        currency_field='currency_id',
        help='Minimum price set by owner'
    )

    # New car-related fields
    vin_number = fields.Char(string='VIN / Chassis Number', help='Vehicle Identification Number')
    registration_number = fields.Char(string='Registration Number', help='Car registration or license plate')
    make = fields.Char(string='Make', help='Car manufacturer, e.g., Toyota, Honda')
    model = fields.Char(string='Model', help='Car model, e.g., Corolla, Civic')
    year = fields.Integer(string='Model Year', help='Year of manufacture')
    color = fields.Char(string='Color', help='Exterior color of the car')
    mileage = fields.Float(string='Mileage (km)', help='Total kilometers driven')
    engine_number = fields.Char(string='Engine Number', help='Unique engine number')
    transmission = fields.Selection([
        ('manual', 'Manual'),
        ('automatic', 'Automatic'),
        ('cvt', 'CVT'),
        ('semi_automatic', 'Semi-Automatic'),
    ], string='Transmission Type', help='Type of transmission system')

    fuel_type = fields.Selection([
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('hybrid', 'Hybrid'),
        ('electric', 'Electric'),
    ], string='Fuel Type', help='Type of fuel the car uses')

    doors = fields.Integer(string='No. of Doors', help='Number of doors')
    seats = fields.Integer(string='No. of Seats', help='Number of seats')
    condition = fields.Selection([
        ('new', 'New'),
        ('used', 'Used'),
        ('damaged', 'Damaged'),
    ], string='Condition', default='used', help='Car condition')

    purchase_date = fields.Date(string='Purchase Date', help='Date when car was received or purchased')
    sale_date = fields.Date(string='Sale Date', help='Date when car was sold')
    sale_price = fields.Monetary(string='Actual Sale Price', currency_field='currency_id')
    # commission_amount = fields.Monetary(string='Commission Earned', currency_field='currency_id',
    #                                     help='Profit earned above the target price')
    commission_amount = fields.Monetary(
        string='Commission Earned',
        currency_field='currency_id',
        compute="_compute_commission_amount",
        store=True,
        help='Profit earned above the target price'
    )

    remarks = fields.Text(string='Additional Notes')
    docs_count = fields.Integer(string="Documents", compute="_compute_docs_count")

    # state = fields.Selection([
    #     ('draft', 'Draft'),
    #     ('sold', 'Sold'),
    # ], string='Status', default='draft', tracking=True)

    # 🧩 Lock Control
    is_locked = fields.Boolean(string='Locked', default=False, readonly=True)
    state = fields.Selection([
        ('draft', 'Unlocked'),
        ('sold', 'Sold / Locked'),
    ], string='Status', default='draft', tracking=True)

    purchaser_id = fields.Many2one(
        'res.partner',
        string='Purchaser',
        help='Customer who purchased the car'
    )
    purchaser_phone = fields.Char(
        string='Purchaser Phone',
        related='purchaser_id.phone',
        readonly=True,
        store=False
    )
    purchaser_email = fields.Char(
        string='Purchaser Email',
        related='purchaser_id.email',
        readonly=True,
        store=False
    )

    def _get_default_sale_date(self):
        return fields.Date.context_today(self)

    # --- Actions (single definitions) ---
    # def action_mark_as_sold(self):
    #     """Mark as sold — validate sale_price first, then set state, date and lock."""
    #     for rec in self:
    #         # server-side validation to prevent invalid state transition
    #         if not rec.sale_price or rec.sale_price <= 0.0:
    #             raise ValidationError(_("Please enter a valid Sale Price (greater than 0) before marking as sold."))
    #         rec.write({
    #             'state': 'sold',
    #             'is_locked': True,
    #             'sale_date': fields.Date.context_today(rec),
    #         })

    invoice_id = fields.Many2one(
        'account.move',
        string='Commission Invoice',
        readonly=True,
        help='Invoice created for this car sale commission.'
    )

    invoice_ids = fields.One2many(
        'account.move',
        'car_id',
        string='Invoices',
        readonly=True,
        help='All invoices created for this car sale commission.'
    )

    # def action_mark_as_sold(self):
    #     for record in self:
    #         if not record.purchaser_id:
    #             raise UserError("Please select a Purchaser before marking as sold.")
    #
    #         if record.state == 'sold':
    #             raise UserError("This car is already marked as sold.")
    #
    #         # Mark as sold
    #         record.state = 'sold'
    #         record.sale_date = fields.Date.today()
    #
    #         # Find sales journal
    #         journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
    #         if not journal:
    #             raise UserError("No Sales Journal found. Please create one before proceeding.")
    #
    #         # Create invoice
    #         invoice_vals = {
    #             'move_type': 'out_invoice',
    #             'partner_id': record.purchaser_id.id,
    #             'invoice_date': fields.Date.today(),
    #             'journal_id': journal.id,
    #             'invoice_line_ids': [(0, 0, {
    #                 'name': f'Commission for Sale of {record.name or "Car"}',
    #                 'quantity': 1,
    #                 'price_unit': record.commission_amount or 0.0,
    #             })],
    #         }
    #         invoice = self.env['account.move'].create(invoice_vals)
    #         invoice.action_post()
    #
    #         # Link the invoice to car
    #         record.invoice_id = invoice.id
    #
    #         # Log message
    #         record.message_post(
    #             body=f"✅ Car marked as sold. "
    #                  f"Invoice <a href='#' data-oe-model='account.move' data-oe-id='{invoice.id}'>"
    #                  f"{invoice.name}</a> created for commission {record.commission_amount}."
    #         )
    #
    #     return {
    #         'type': 'ir.actions.client',
    #         'tag': 'display_notification',
    #         'params': {
    #             'title': 'Car Sold',
    #             'message': f'Invoice {invoice.name} created for commission {record.commission_amount}.',
    #             'type': 'success',
    #             'sticky': False,
    #         }
    #     }

    def action_mark_as_sold(self):
        for record in self:
            if not record.purchaser_id:
                raise UserError("Please select a Purchaser before marking as sold.")

            if record.state == 'sold':
                raise UserError("This car is already marked as sold.")

            # Mark as sold
            record.state = 'sold'
            record.sale_date = fields.Date.today()

            # Create invoice for commission
            journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
            if not journal:
                raise UserError("No Sales Journal found. Please create one before proceeding.")

            invoice_vals = {
                'move_type': 'out_invoice',
                'partner_id': record.purchaser_id.id,
                'invoice_date': fields.Date.today(),
                'journal_id': journal.id,
                'car_id': record.id,  # 🔗 link to car
                'invoice_line_ids': [(0, 0, {
                    'name': f'Commission for Sale of {record.name or "Car"}',
                    'quantity': 1,
                    'price_unit': record.commission_amount or 0.0,
                })],
            }

            invoice = self.env['account.move'].create(invoice_vals)
            invoice.action_post()
            record.invoice_id = invoice.id  # 🔗 store reference on car

            # Don’t auto-post; let user post manually
            record.message_post(
                body=f"✅ Car marked as sold. Draft Invoice <a href='#' data-oe-model='account.move' data-oe-id='{invoice.id}'>#{invoice.name}</a> created for commission {record.commission_amount}."
            )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Car Sold'),
                'message': _('The car has been marked as sold and the invoice has been created.'),
                'type': 'success',
                'sticky': False,
            }
        }, {'type': 'ir.actions.client', 'tag': 'reload'}

    # def action_set_to_draft(self):
    #     """Revert car back to draft state"""
    #     for rec in self:
    #         rec.write({
    #             'state': 'draft',
    #             'sale_date': False,
    #             'is_locked': False
    #         })

    def action_set_to_draft(self):
        """Revert car back to draft state, only if related invoice is in draft."""
        for rec in self:
            # Check if car is sold/locked
            if rec.state == 'sold':
                if rec.invoice_id:
                    # If invoice exists and is not draft, block it
                    if rec.invoice_id.state != 'draft':
                        raise UserError(_(
                            "You cannot set this car to draft because the related invoice "
                            "is posted. Please set the invoice to Draft first."
                        ))
                else:
                    raise UserError(_(
                        "This car is marked as sold but has no related invoice. "
                        "Please check the car’s invoice before resetting."
                    ))

            # If validation passes → reset to draft
            rec.write({
                'state': 'draft',
                'sale_date': False,
                'is_locked': False
            })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Car Set to Draft',
                'message': 'The car has been successfully reverted to draft state.',
                'type': 'success',
                'sticky': False,
            }
        }, {'type': 'ir.actions.client', 'tag': 'reload'}

    @api.depends('sale_price', 'target_price')
    def _compute_commission_amount(self):
        for rec in self:
            rec.commission_amount = (rec.sale_price or 0) - (rec.target_price or 0)

    def action_view_invoice(self):
        self.ensure_one()
        if not self.invoice_id:
            raise UserError(_("No invoice found for this car."))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.invoice_id.id,
            'target': 'current',
        }

    def action_view_invoices(self):
        self.ensure_one()
        return {
            'name': f"Invoices for {self.name}",
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('car_id', '=', self.id)],
            'context': {'default_car_id': self.id},
            'target': 'current',
        }

    # def action_view_invoices(self):
    #     self.ensure_one()
    #     return {
    #         'name': f"Invoices for {self.name}",
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'account.move',
    #         'view_mode': 'tree,form',
    #         'views': [
    #             (self.env.ref('account.view_move_tree').id, 'tree'),
    #             (self.env.ref('account.view_move_form').id, 'form')
    #         ],
    #         'domain': [('car_id', '=', self.id)],
    #         'context': {'default_car_id': self.id},
    #         'target': 'current',
    #     }

    # # Actions
    # def action_mark_as_sold(self):
    #     for rec in self:
    #         rec.write({
    #             'state': 'sold',
    #             'is_locked': True,
    #             'sale_date': fields.Date.context_today(self),
    #         })

    def action_unlock_car(self):
        for rec in self:
            rec.write({
                'state': 'draft',
                'is_locked': False,
            })

    # --- Server-side constraint (enforces always, even if someone writes directly) ---
    @api.constrains('state', 'sale_price')
    def _check_sale_price_positive(self):
        for rec in self:
            if rec.state == 'sold' and (not rec.sale_price or rec.sale_price <= 0.0):
                raise ValidationError(_("Sale Price must be greater than zero for sold cars."))

    # Optional: guard write so any attempt to write state -> sold must include sale_price
    def write(self, vals):
        # If someone tries to set state to 'sold' through write, validate.
        if vals.get('state') == 'sold':
            # check sale_price provided in vals or existing record
            for rec in self:
                sale_price = vals.get('sale_price', rec.sale_price)
                if not sale_price or sale_price <= 0.0:
                    raise ValidationError(_("Sale Price must be greater than zero when setting the car to Sold."))
        return super(ProductTemplate, self).write(vals)

# class ProductProduct(models.Model):
#     _inherit = 'product.product'
#
#     owner_id = fields.Many2one(
#         'res.partner',
#         string='Car Owner',
#         related='product_tmpl_id.owner_id',
#         store=True,
#         readonly=False
#     )




    expense_ids = fields.One2many(
        'account.move', 'car_id',
        string="Expenses",
        domain=[('move_type', '=', 'in_invoice')],
        help="Vendor bills (expenses) related to this car."
    )

    expense_count = fields.Integer(string='Expense Count', compute='_compute_expense_count')
    company_id = fields.Many2one(
        'res.company', string="Company",
        default=lambda self: self.env.company
    )

    @api.depends('expense_ids')
    def _compute_expense_count(self):
        for record in self:
            record.expense_count = len(record.expense_ids)

    def action_view_expenses(self):
        self.ensure_one()
        return {
            'name': f'Expenses for {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('car_id', '=', self.id), ('move_type', '=', 'in_invoice')],
            'context': {'default_car_id': self.id, 'default_move_type': 'in_invoice'},
            'target': 'current',
        }

    expense_id = fields.One2many('car.expense', 'car_id', string="Expenses")
