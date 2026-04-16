# -*- coding: utf-8 -*-

{
    'name': "POS Products by Sequence Number",
    'summary': """Arrange POS products based on a sequence number.""",
    'description': """
        Arrange and prioritize products in the Odoo POS interface with ease.
        This module allows users to define a custom display order for products on the POS screen using a dedicated 
        "POS Sequence" field. With this feature, businesses can highlight fast-moving items, promote specific products, 
        or maintain a visually organized layout for quicker checkout operations.

        Key Features:
        • Add and manage POS sequence numbers on products  
        • Display POS products in as per given sequences 
        • Offers better product visibility and efficient POS operations  
        • Works seamlessly with Odoo Point of Sale 
        
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
        'views/product_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'cst_pos_products_by_sequences/static/src/product_screen.js',
        ]
    },
    "images": ["static/description/Banner.png"],
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "auto_install": False,
}
