# -*- coding: utf-8 -*-

{
    'name': "POS Hide Product Info Button",
    'summary': """Control the visibility of product information in Odoo POS to protect sensitive data.""",
    'description': """
        The POS Hide Product Information module for Odoo allows businesses to manage the visibility 
        of sensitive product details in the Point of Sale interface.

        Key Features:
        * Add a setting in POS configuration to hide or show the Product Info ('i') button at shop level.
        * Helps protect sensitive or unnecessary product data from being viewed in the POS.
        * Keeps the POS interface clean, simple, and focused for cashiers.
        
    """,
    "author": "CodeSphere Tech",
    "website": "https://www.codespheretech.in/",
    "category": "Point of Sale",
    "version": "18.0.1.0.0",
    "sequence": 0,
    "currency": "USD",
    "price": "0.00",
    "depends": ["point_of_sale"],
    'data': [
        'views/res_config_setting_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'cst_pos_hide_product_info_btn/static/src/product_screen.xml',
        ]
    },
    "images": ["static/description/Banner.png"],
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "auto_install": False,
}
