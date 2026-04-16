# Powered by Sensible Consulting Services
# -*- coding: utf-8 -*-
# © 2025 Sensible Consulting Services (<https://sensiblecs.com/>)
from odoo import api, fields, models


class SBLHrEmployee(models.Model):
    _inherit = 'hr.employee'

    # POS Actions Popup - Restaurant Actions
    sbl_hide_pos_action_split = fields.Boolean(
        string='Hide Split Button',
        help='If checked, the Split button will be hidden in the Actions popup.',
        default=False,
    )
    sbl_hide_pos_action_guests = fields.Boolean(
        string='Hide Guests Button',
        help='If checked, the Guests button will be hidden in the Actions popup.',
        default=False,
    )
    sbl_hide_pos_action_transfer_merge = fields.Boolean(
        string='Hide Transfer/Merge Button',
        help='If checked, the Transfer/Merge button will be hidden in the Actions popup.',
        default=False,
    )
    sbl_hide_pos_action_bill = fields.Boolean(
        string='Hide Bill Button',
        help='If checked, the Bill button will be hidden in the Actions popup.',
        default=False,
    )
    sbl_hide_pos_action_edit_order_name = fields.Boolean(
        string='Hide Edit Order Name Button',
        help='If checked, the Edit Order Name button will be hidden in the Actions popup.',
        default=False,
    )
    sbl_hide_pos_action_switch_dine_takeaway = fields.Boolean(
        string='Hide Switch Dine in/Takeaway Button',
        help='If checked, the Switch to Dine in/Takeaway button will be hidden in the Actions popup.',
        default=False,
    )
    sbl_hide_restaurant_order_button = fields.Boolean(
        string='Hide Order Button',
        help='If checked, the Order button will be hidden in the restaurant POS actionpad.',
        default=False,
    )
    sbl_hide_restaurant_plan_button = fields.Boolean(
        string='Hide Plan Button',
        help='If checked, the Plan button will be hidden in the restaurant POS navbar.',
        default=False,
    )
    sbl_hide_pos_switch_floor_view = fields.Boolean(
        string='Hide Switch Floor View',
        help='If checked, the Switch Floor View option will be hidden in the POS menu.',
        default=False,
    )
    sbl_disabled_floor_ids = fields.Many2many(
        'restaurant.floor',
        'sbl_hr_employee_disabled_floor_rel',
        'employee_id',
        'floor_id',
        string='Disabled Floors',
        help='Select floors that should be hidden/disabled for this employee in the restaurant POS.',
    )

    @api.model
    def _load_pos_data_fields(self, config_id):
        fields = super()._load_pos_data_fields(config_id)
        return fields + [
            'sbl_hide_pos_action_split', 'sbl_hide_pos_action_guests',
            'sbl_hide_pos_action_transfer_merge', 'sbl_hide_pos_action_bill',
            'sbl_hide_pos_action_edit_order_name', 'sbl_hide_pos_action_switch_dine_takeaway',
            'sbl_hide_restaurant_order_button', 'sbl_hide_restaurant_plan_button',
            'sbl_hide_pos_switch_floor_view', 'sbl_disabled_floor_ids'
        ]
