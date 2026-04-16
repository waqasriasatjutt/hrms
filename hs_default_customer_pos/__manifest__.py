# -*- coding: utf-8 -*-
{
    'name': 'Default Customer on POS',
    'version': '18.0.1.0',
    'author': 'HSxTECH',
    'category': 'Point of Sale',
    'depends': ['point_of_sale'],
    'summary': 'This module allows you to set a default customer in the Point of Sale (POS) system, helping cashiers save time during order creation. By automatically assigning a pre-configured customer to new POS orders, it streamlines the checkout process, reduces repetitive manual selection, and increases overall efficiency in busy retail environments.',
    'description': """
This module allows you to set a default customer in the Point of Sale (POS) system, helping cashiers save time during order creation. By automatically assigning a pre-configured customer to new POS orders, it streamlines the checkout process, reduces repetitive manual selection, and increases overall efficiency in busy retail environments.
    """,
    'data': [
        'views/pos_config_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'hs_default_customer_pos/static/src/js/**/*',
        ],
    },
    'application': True,
    'installable': True,
    "license": "LGPL-3",
    "images":
        [
            'static/description/banner.gif',
            'static/description/icon.png',
        ], }
