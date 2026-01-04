# -*- coding: utf-8 -*-
# Part of Simple Online Users. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    online_users_visibility_group = fields.Selection([
        ('base.group_system', 'System Administrators'),
        ('base.group_user', 'All Internal Users'),
        ('base.group_portal', 'Portal Users'),
    ], string='Who can see Online Users',
    config_parameter='online_users.visibility_group',
    default='base.group_system',
    help='Users in this group will see the online users count in systray')
