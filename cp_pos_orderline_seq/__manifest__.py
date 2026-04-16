# -*- coding: utf-8 -*-
#
#  ┌────────────────────────────────────────────────────────────────────┐
#  │   Developed by: CHEF PIXEL                                         │
#  │   Website: https://chef-pixel.fr                                   │
#  │   Support: hello@chef-pixel.fr                                     │
#  │   Description: Add sequence numbers to POS order lines             │
#  └────────────────────────────────────────────────────────────────────┘
#
#  🔢 Improve readability and tracking in POS orders with line sequences!

{
    "name": "POS Orderline Sequence",
    "version": "18.0.0.0",
    "summary": "Add sequence numbers to POS order lines",
    "description": """
        POS Orderline Sequence
        ======================

        This module enhances the Point of Sale interface by adding sequence
        numbers to each order line. It improves usability and readability
        for both front-end users and printed receipts.

        Key Features
        ------------
        - Assigns sequence numbers to each line in a POS order
        - Enhances visual clarity in POS interface
        - Useful for long or detailed orders

        Ideal for:
        - Restaurants, retailers, or service points with complex POS orders
        - Businesses looking to improve order traceability in POS
    """,
    "author": "CHEF PIXEL",
    "maintainer": "CHEF PIXEL",
    "support": "hello@chef-pixel.fr",
    "company": "CHEF PIXEL",
    "website": "https://chef-pixel.fr",
    "category": "Point of Sale",
    "license": "LGPL-3",
    "depends": ["point_of_sale"],
    "data": [],
    "assets": {
        "point_of_sale._assets_pos": [
            "cp_pos_orderline_seq/static/src/app/generic_components/orderline/orderline.xml",
            "cp_pos_orderline_seq/static/src/app/generic_components/orderline/orderline.js",

            "cp_pos_orderline_seq/static/src/app/models/pos_order_line.js",
            "cp_pos_orderline_seq/static/src/app/models/pos_order.js",

            "cp_pos_orderline_seq/static/src/app/store/pos_store.js",
        ],
    },
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": False,
    "auto_install": False
}