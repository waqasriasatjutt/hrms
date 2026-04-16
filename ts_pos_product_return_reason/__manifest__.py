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

{
    'name': 'POS Product Return Reason',
    'version': '18.0.1.0.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Streamline returns in Odoo POS with a dedicated master, quick reason selection, and full backend traceability.',
    'description': 'The POS Return Reason app adds a structured way to manage product returns in Odoo POS. With a dedicated master, quick reason selection in POS, and automatic recording in backend orders, it ensures clarity, consistency, and better insights for return handling.',
    'author': 'Techvaria',
    'company': 'Techvaria',
    'maintainer': 'Techvaria',
    'website': 'https://techvaria.com',
    'depends': ['point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_return_reason_views.xml',
        'views/pos_order_views.xml',
    ],
    "assets": {
        "point_of_sale._assets_pos": ["ts_pos_product_return_reason/static/src/**/*"],
    },
    'images': [
        'static/description/screen.jpg',
    ],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
}
