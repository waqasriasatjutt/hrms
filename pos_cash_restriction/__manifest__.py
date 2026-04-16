# -*- coding: utf-8 -*-

{
    'name': 'POS - Cash Out Restriction',
    'version': '1.0',
    'summary': """Restrict cash-out operations in POS when the amount exceeds the available cash balance. 
            keywords: cash restriction | POS cash out restriction | Cash control POS | POS cash register limit | Restrict cash withdrawals | cash register limit | cash limit""",
    'description': """This module adds a restriction to prevent users from withdrawing more cash than what is available in the POS cash register. 
            It displays the current available amount and blocks excessive withdrawals.""",
    'category': 'Point of Sale',
    'author': 'Dustin Mimbela',
    'depends': ['point_of_sale'],
    'data': ['views/res_config_settings_view.xml'],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_cash_restriction/static/src/**/*',
        ],
    },
    'images': ['static/description/banner.gif'],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
