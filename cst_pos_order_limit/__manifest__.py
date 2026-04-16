# -*- coding: utf-8 -*-

{
    "name": "POS Order Limit",
    "summary": "Block creation of new POS orders when the active order limit is reached",
    "description": """
        This module allows you to control the number of active (open) orders in the Point of Sale.

        Once the configured order limit is reached, POS users will not be able to create new orders
        until existing orders are completed or cancelled. The restriction is enforced globally
        across the POS interface, including all order creation entry points.
        
        When a user attempts to create an order beyond the allowed limit, a warning dialog is shown
        to clearly inform them about the restriction.

        Key Features:
        - Set a maximum number of active POS orders
        - Prevent creation of new orders when the limit is reached
        - Warning dialog displayed when the limit is exceeded
        - Enforced globally across the POS interface
        - Simple configuration from POS settings

    """,
    "author": "CodeSphere Tech",
    "website": "https://www.codespheretech.in/",
    "category": 'Point Of Sale',
    "version": "18.0.1.0.0",
    'sequence': 0,
    "currency": "USD",
    "price": "0",
    "depends": ["point_of_sale", ],
    "data": [
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "cst_pos_order_limit/static/src/**/*",
        ],
    },
    "images": ["static/description/Banner.png"],
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "auto_install": False,
}
