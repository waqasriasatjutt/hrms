# -*- coding: utf-8 -*-

{
    'name': 'POS Order Line Sequence Number',
    'summary': 'Display sequence numbers for order lines in Point of Sale',
    'description': """
        This module adds sequence numbers to order lines in the Odoo Point of Sale interface.

        Each order line in the POS screen is automatically numbered in the order it is added,
        helping cashiers and staff quickly identify, reference, and review items during
        order processing.

        Key Features:
        - Displays sequence numbers for POS order lines
        - Can be enabled or disabled per Point of Sale configuration
        - Automatically updates numbering when items are added or removed
        - Lightweight and frontend-only implementation

    """,
    "author": "CodeSphere Tech",
    "website": "https://www.codespheretech.in/",
    "category": "Point of Sale",
    "version": "18.0.1.0.0",
    "sequence": 0,
    "currency": "USD",
    "price": "0.00",
    'depends': ['point_of_sale', ],
    'data': [
        'views/res_config_setting_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'cst_pos_orderline_seq/static/src/xml/pos_order_line.xml',
            'cst_pos_orderline_seq/static/src/js/pos_order_line.js',
            'cst_pos_orderline_seq/static/src/js/pos_order.js',
            'cst_pos_orderline_seq/static/src/js/pos_store.js',
        ],
    },
    'images': ['static/description/Banner.png'],
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "auto_install": False
}
