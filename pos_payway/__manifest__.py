# -*- coding: utf-8 -*-
# Copyright (C) 2024 Axcelere.
# Licensed under the GPL-3.0 License or later.

{
    "name": "POS Payway",
    "summary": """
        Integrate your POS with a Payway payment terminal
    """,
    "author": "Axcelere",
    "website": "https://www.axcelere.com",
    "category": "Sales/Point of Sale",
    "version": "18.0.0.1",
    "depends": [
        "point_of_sale",
        "pos_credit_card_installment",
    ],

    "data": [
        'security/ir.model.access.csv',
        'views/pos_payway_credential_views.xml',
        'views/pos_payment_method_views.xml',
        'views/pos_config_views.xml',
        'views/payway_log_views.xml',
    ],

    "assets": {
        "point_of_sale._assets_pos": [
            "pos_payway/static/**/*",
            'pos_payway/static/src/xml/**/*.xml',
        ],
    },

    "images": [
        "static/description/icon.png"
    ],

    "installable": True,
    "license": "GPL-3",
}
