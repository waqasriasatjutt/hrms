# -*- coding: utf-8 -*-
{
    "name": "POS Total Product Display",
    "author": "AskByte Technolab",
    "summary": """POS Total Product Display.""",
    "description": """
        Display the total number of products in the category on the POS interface.
    """,
    "category": "Point of Sale",
    "version": "18.0.1.0",
    "depends": ["point_of_sale"],
    "data":["views/res_config_settings_views.xml"],
    "assets": {
        "point_of_sale._assets_pos": [
            "abt_pos_total_product_display/static/src/app/screens/product_screen.xml",
        ],
    },
    "images": ["static/description/thumbnail.png"],
    "license": "LGPL-3",
    "application": True,
    "auto_install": False,
}
