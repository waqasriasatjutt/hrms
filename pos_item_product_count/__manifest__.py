# -*- coding: utf-8 -*-
{
    "name": "POS Item, Product & Quantity Counter",
    "summary": "Show unique products, total lines, and total quantity in Point of Sale order summary",
    "description": """
        POS Item, Product & Quantity Counter enhances Odoo Point of Sale by displaying
        real-time order statistics directly in the POS interface.

        Key Features:
        • Displays total quantity of items in the order
        • Shows total number of order lines
        • Calculates unique products added to the order
        • Updates dynamically as products are added or removed

    """,
    "author": "Upstackers Technologies",
    "website": "https://upstackers.com/",
    "category": "Point of Sale",
    "version": "18.1",
    "depends": ["base", "point_of_sale",],
    "data": [
        # No backend views required
    ],
    'assets': {
        'point_of_sale.base_app': [
            'pos_item_product_count/static/src/app/generic_components/order_widget/order_widget.xml',
            'pos_item_product_count/static/src/app/generic_components/order_widget/order_widget.js',
            'pos_item_product_count/static/src/app/pos.scss',
        ],
    },
    "images": [
        "static/description/banner.png",
        "static/description/icon.png",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "LGPL-3",
}