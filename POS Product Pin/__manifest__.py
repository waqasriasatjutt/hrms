# -*- coding: utf-8 -*-
{
    'name': "POS Product Pin",
    'summary': "Pin important products in Point of Sale for quick access",
    'description': """
        This module allows you to prioritize products in the Point of Sale 
        interface, making it easier for cashiers and sales staff to quickly 
        access the most important products. 

        Features:
        - Highlight or pin important products in the POS.
        - Arrange product visibility in order of importance.
        - Fully integrated with Odoo's Point of Sale and Product modules.
        - Improves efficiency in busy sales environments by reducing search time.
    """,
    'author': "Micra Digital",
    'website': "https://www.micra.digital",
    'support': "hello@micra.digital",
    'license': "OPL-1",
    'category': 'Point of Sale',
    'version': '18.0.1.0.0',
    'depends': ['base', 'point_of_sale', 'product'],
    'data': [
        # Add XML/CSV files here if you later define menus, security, or data
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'product_pin/static/src/js/product_card.js',
            'product_pin/static/src/js/product_screen.js',
            'product_pin/static/src/xml/product_screen.xml',
            'product_pin/static/src/xml/product_card.xml',
            'product_pin/static/src/js/combo_configure_popup.js',
            'product_pin/static/src/xml/combo_configure_popup.xml',
        ],
    },
    'demo': [
        # You can add demo data here if needed, e.g., 'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'images': [
        'static/description/banner.png',
    ],
    'maintainer': 'Micra Digital',
    'currency': 'USD',
}
