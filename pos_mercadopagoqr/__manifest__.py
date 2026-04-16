# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Pos MP QR",
    "summary": """
        Integrate your POS with a Mp
    """,
    "description": """
Allow to pay with MP
==============================

This module allows customers to pay for their orders with credit
cards. The transactions are processed by MP (developed by Axcelere). 
    """,
    "author": "Axcelere",
    "website": "https://www.axcelere.com",
    "category": "Sales/Point of Sale",
    "version": "18.0.0.0",
    "depends": [
        "point_of_sale",
        "pos_mercadopago",
    ],

    'data': [
        'views/pos_payment_method_views.xml',
        'views/mp_store_box_views.xml',
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_mercadopagoqr/static/**/*",
            'pos_mercadopagoqr/static/src/xml/**/*.xml',
        ],
    },
    "installable": True,
    "license": "GPL-3",
}
