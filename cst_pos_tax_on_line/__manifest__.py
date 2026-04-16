# -*- coding: utf-8 -*-
{
    "name": "POS Tax per Order Line",
    "summary": "Show tax amount per POS order line and on the receipt",
    "description": """
        This module displays the applied tax amount for each POS order line and
        shows the same tax amount on the POS receipt.

        It helps POS users clearly understand how much tax is applied to each
        product line instead of only viewing the total tax at the order level.

        Key Highlights:
        - Displays tax amount per POS order line
        - Shows line-wise tax amounts on the POS receipt
        - Improves tax transparency for POS users
        - Useful for GST-compliant POS setups

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
        'views/res_config_settings_views.xml',
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "cst_pos_tax_on_line/static/src/**/*",
        ],
    },
    "images": ["static/description/Banner.png"],
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "auto_install": False,
}