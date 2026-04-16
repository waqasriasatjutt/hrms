# -*- coding: utf-8 -*-
#############################################################################
#
#    Techvaria Solutions Pvt. Ltd.
#
#    Copyright (C) 2025-Techvaria Solutions(<https://techvaria.com>)
#    Author: Techvaria Solutions Pvt. Ltd.(info@techvaria.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo import models, fields


class POSReturnReason(models.Model):
    """ Class for return reason"""
    _name = 'pos.return.reason'
    _inherit = 'mail.thread'
    _description = 'POS Return Reason'
    _order = 'sequence asc'

    sequence = fields.Integer(default=1)
    name = fields.Char(string='Reason', required=True, tracking=True)
    active = fields.Boolean(default=True, tracking=True)
    description = fields.Text(tracking=True, translate=True)

    _sql_constraints = [
        ('pos_product_return_reason_name_unique',
         'UNIQUE(name)',
         'The Reason must be unique'),
    ]
