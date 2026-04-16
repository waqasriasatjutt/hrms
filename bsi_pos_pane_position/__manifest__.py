# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2025-today Botspot Infoware Pvt. Ltd. <www.botspotinfoware.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################
{
    'name': "POS Screen/Pane Position",
    'author': 'Botspot Infoware Pvt. Ltd.',
    'category': 'Point of Sale',
    'summary': """This Odoo App helps to add the feature to configure pos screen/pane position by single click.""",
    'website': 'https://www.botspotinfoware.com',
    'company': 'Botspot Infoware Pvt. Ltd.',
    'maintainer': 'Botspot Infoware Pvt. Ltd.',
    'description': """This Odoo App add functionality to add configuration of pos screen/pane position, with this configuration the position of screen/pane can be changed to Left or Right""",
    'version': '18.1',
    'depends': ['base', 'point_of_sale'],
    'data': [
        'views/pos_config_view.xml',
        ],
    'images': [],
    'assets': {
        'point_of_sale._assets_pos': [
            'bsi_pos_pane_position/static/src/xml/Screens/ProductScreen/ProductScreen.xml',
            
        ],
        'web.assets_qweb': []
        },
    "images": ['static/description/Banner.gif'],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
