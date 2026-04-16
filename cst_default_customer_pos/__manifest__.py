# -*- coding: utf-8 -*-

{
    "name": "PoS Default Customer",
    "summary": "Automatically set a default customer in Point of Sale.",
    "description": """
        This module allows you to automatically assign a default customer
        in the Odoo Point of Sale.

        ✔ Set a default customer for POS orders  
        ✔ Automatically applied when POS starts  
        ✔ Ideal for walk-in or cash customers  
        ✔ Reduces manual customer selection  
        ✔ Improves cashier speed and accuracy    
        
    """,
    "author": "CodeSphere Tech",
    "website": "https://www.codespheretech.in/",
    "category": "Point Of Sale",
    "version": "18.0.1.0.0",
    "currency": "USD",
    "price": "0.00",
    "depends": ["point_of_sale"],
    "data": [
        "views/res_config_views.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "cst_default_customer_pos/static/src/js/pos_order.js",
        ],
    },
    "images": ["static/description/Banner.png"],
    "license": "LGPL-3",
    "installable": True,
    "application": True,
    "auto_install": False,
}
