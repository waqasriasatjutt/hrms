# -*- coding: utf-8 -*-
{
    'name': 'Restrict Zero Price Products',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Restrict zero price products in POS with visual indicators, validation errors, and disabled validate button',
    'description': """
Restrict POS Order Line with Zero Price

This addon provides comprehensive zero price product restrictions in Point of Sale:

Key Features:
• Visual highlighting of zero price products in red
• Configurable restriction settings in POS configuration
• Validation warnings when attempting to process zero price products
• Disabled validate button when zero price products are present
• Clear user feedback about restricted products
• Multi-language support (English/French)

The addon helps prevent accidental sales of products with zero or negative prices while providing clear visual indicators and user-friendly error messages.
    """,
    'author': 'HSXTech',
    'website': 'https://hsxtech.net',
    'depends': ['base', 'point_of_sale'],
    'data': [
        'views/pos_config_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'hs_pos_restrict_zero_price/static/src/css/pos_zero_price.css',
            'hs_pos_restrict_zero_price/static/src/app/models.js',
        ],
    },
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
    'live_test_url': 'https://hsxtech.net',
    "images":
        [
            'static/description/banner.gif',
            'static/description/icon.png',
        ], }
