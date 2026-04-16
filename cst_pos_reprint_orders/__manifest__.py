# -*- coding: utf-8 -*-

{
    "name": "POS Order Receipt Reprint",
    'summary': """"Easily reprint POS receipts directly from the Order Screen.""",
    "description": """
        This module adds a 'print' icon to the POS Order Screen, allowing users to 
        manually reprint any order receipt without reopening the session or order.
        
        - Reprint POS receipts directly from the order list.
        - Fully compatible with the default Odoo POS UI.
        - Works seamlessly with Odoo Community and Enterprise editions.
        - No popups or custom dialogs — uses native Odoo behavior.
    """,
    "author": "CodeSphere Tech",
    "website": "https://www.codespheretech.in/",
    "category": 'Point Of Sale',
    "version": "18.0.1.0.0",
    'sequence': 0,
    "currency": "USD",
    "price": "0",
    "depends": ['point_of_sale', ],
    "data": [],
    'assets': {
        'point_of_sale._assets_pos': [
            'cst_pos_reprint_orders/static/src/**/*',
        ],
    },
    'images': ['static/description/Banner.png'],
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "auto_install": False,
}

