# -*- coding: utf-8 -*-
{
    'name': "POS Product Vendor Info",
    'version': '18.0.1.0.1',
    'category': 'Point of Sale',
    'summary': """POS Product Vendor Info""",
    'description': """POS Product Vendor Info""",
    'author': 'Visnu',
    'price': '0',
    'currency': 'USD',
    'depends': [
        'point_of_sale',
    ],
    'data': [
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'vis_pos_product_vendor_info/static/src/**/*',
        ],
    },
    'images': ['static/description/icon.png'],
    'license': 'OPL-1',
    'installable': True,
    'application': False,
}