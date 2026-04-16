# -*- coding: utf-8 -*-
{
    'name': 'POS Pay Customers',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Create payments to customers in POS with general note support',
    'description': """
        This module allows creating payments to customers directly from the POS Customer screen.
        It integrates with pos_general_note to generate a note upon payment.
    """,
    'author': 'HSxTech',
    'depends': ['point_of_sale', 'pos_settle_due', ],
    'data': [],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_pay_customers/static/src/**/*',
        ],
    },
    "images": [
        "static/description/banner.gif",
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
