# -*- coding: utf-8 -*-

{
    "name": "POS Quick Reorder",
    "summary": "Quickly reorder previous POS orders with a single click.",
    "description": """
        POS Quick Reorder allows cashiers to instantly recreate a previous order
        directly from the POS order history.

        This feature is ideal for repeat customers and fast-paced environments,
        eliminating the need to manually add products again.

        Key Features:
        - Reorder completed POS orders from the order list.
        - Recreates order lines using the same product variants and quantities.
        - Skips product configurator for faster checkout.
        - Uses native Odoo POS behavior (no popups or custom dialogs).
        - Fully compatible with Odoo Community and Enterprise editions.
        
    """,
    "author": "CodeSphere Tech",
    "website": "https://www.codespheretech.in/",
    "category": "Point Of Sale",
    "version": "18.0.1.0.0",
    "sequence": 0,
    "currency": "USD",
    "price": "0",
    "depends": ["point_of_sale"],
    "data": [],
    "assets": {
        "point_of_sale._assets_pos": [
            "cst_pos_reorder/static/src/**/*",
        ],
    },
    "images": ["static/description/Banner.png"],
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "auto_install": False,
}
