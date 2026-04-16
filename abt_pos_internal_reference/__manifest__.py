# -*- coding: utf-8 -*-
{
    'name': 'POS Internal References',
    'author': "AskByte Technolab",
    'summary': """Added internal references for improved tracking.""",
    'description': """
        Internal references are now integrated into the Product Screen, Order Lines, 
        and Receipts, enhancing product management and accuracy throughout transactions.
    """,
    'category': 'Point of Sale',
    'version': '18.0.1.0',
    'depends': ['point_of_sale'],
    'assets': {
        'point_of_sale._assets_pos': [
            'abt_pos_internal_reference/static/src/app/screens/product_screen/product_screen.js',
            'abt_pos_internal_reference/static/src/app/models/pos_order_line.js'
        ],
    },
    'images': ['static/description/thumbnail.gif'],
    'license': 'LGPL-3',
    'application': True,
    'auto_install': False,
}
