# -*- coding: utf-8 -*-
{
    'name': 'POS Hide Odoo Branding(Screen & Receipt)',
    "summary": "Remove Odoo branding from POS Screen & Receipts for a clean, white-label POS interface.",
    'description': """
        This module hides all default Odoo branding elements from the Point of Sale (POS) interface, including
        the "Powered by Odoo" message on the POS receipt and Odoo branding on the POS screen.

        It helps businesses maintain a clean, professional, and white-label POS environment without modifying
        any core Odoo files.

        Key Features:
        ✔ Remove "Powered by Odoo" from POS Receipts  
        ✔ Hide Odoo branding from POS Screen  
        ✔ Lightweight and does not override core files  
        ✔ Auto-applied after installation (no configuration required)  
        ✔ Compatible with custom POS themes and layouts  

    """,
    "author": "CodeSphere Tech",
    "website": "https://www.codespheretech.in/",
    "category": "Point of Sale",
    "version": "18.0.1.0.1",
    "sequence": 0,
    "currency": "USD",
    "price": "0",
    "depends": ["point_of_sale", ],
    "data": [
    ],
    "assets": {
        'point_of_sale._assets_pos': [
            'cst_pos_hide_odoo_branding/static/src/xml/hide_odoo_screen_receipt.xml',
        ],
        'point_of_sale.customer_display_assets': [
            'cst_pos_hide_odoo_branding/static/src/scss/customer_display.scss',
        ],
    },
    "images": ["static/description/Banner.png"],
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "auto_install": False,
}
