# Powered by Sensible Consulting Services
# -*- coding: utf-8 -*-
# © 2025 Sensible Consulting Services (<https://sensiblecs.com/>)

from odoo import fields, models


class ScPosConfig(models.Model):
    _inherit = 'pos.config'

    sbl_create_timesheet = fields.Boolean(
        string='Create Timesheet',
        help='Enable automatic timesheet creation when POS session starts/stops',
        default=False
    )