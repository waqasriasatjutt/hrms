# -*- coding: utf-8 -*-
from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    zk_user_id = fields.Char(
        'ZKTeco User ID',
        index=True,
        help='PIN enrolled on the ZKTeco biometric device. '
             'Leave empty to fall back to the employee barcode.',
        groups='hr.group_hr_user',
    )
