# booking_request_system/models/booking_request.py
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class BookingRequest(models.Model):
    _name = "booking.request"
    _description = "Booking Request"
    _order = "check_in asc"

    room_id = fields.Many2one("hotel.room", string="Room", required=True)
    customer = fields.Char("Customer", required=True)
    check_in = fields.Datetime("Check-in", required=True)
    check_out = fields.Datetime("Check-out", required=True)
    status = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"), ("canceled", "Canceled")],
        string="Status",
        default="draft",
        required=True,
        tracking=True,
    )
    comment = fields.Text("Comment")

    # For calendar color coding
    color = fields.Integer("Color", compute="_compute_color", store=True)

    @api.depends("status")
    def _compute_color(self):
        # Use Odoo's 0..11 palette indexes
        # map: draft -> gray(0), confirmed -> green(10), canceled -> red(1)
        mapping = {"draft": 0, "confirmed": 10, "canceled": 1}
        for rec in self:
            rec.color = mapping.get(rec.status, 0)

    @api.constrains("check_in", "check_out")
    def _check_dates(self):
        for rec in self:
            if rec.check_in and rec.check_out and rec.check_out <= rec.check_in:
                raise ValidationError(_("Check-out must be later than Check-in."))

    # Ensure Gantt shows ALL rooms even if no bookings (important!)
    @api.model
    def _read_group_room_id(self, rooms, domain, order):
        return self.env["hotel.room"].search([])

    room_id.group_expand = _read_group_room_id

    # Action buttons
    def action_confirm(self):
        for rec in self:
            if rec.status == "draft":
                rec.status = "confirmed"

    def action_cancel(self):
        for rec in self:
            if rec.status in ("draft", "confirmed"):
                rec.status = "canceled"

    def action_restore(self):
        for rec in self:
            if rec.status == "canceled":
                rec.status = "draft"
