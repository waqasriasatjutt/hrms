# Powered by Sensible Consulting Services
# -*- coding: utf-8 -*-
# © 2025 Sensible Consulting Services (<https://sensiblecs.com/>)

from odoo import fields, models


class ScHrAttendance(models.Model):
    _inherit = 'hr.attendance'

    sbl_pos_session_id = fields.Many2one(
        'pos.session',
        string='POS Session',
        help='Related POS session for this timesheet entry'
    )