# -*- coding: utf-8 -*-
{
    "name": "Implent in pos credit card installment",
    "summary": "",
    "description": """""",
    "author": "Axcelere",
    "website": "http://www.axcelere.com",
    "category": "pos",
    "version": "18.0.0.0.1",
    "depends": ['card_installment', 'point_of_sale'],
    "data": [
        "views/pos_payment_method.xml",
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_credit_card_installment/static/src/css/pos_card_cart_installment.css',
            'pos_credit_card_installment/static/src/overrides/models/pos_simple.js',
            'pos_credit_card_installment/static/src/overrides/screens/**/*.js',
            'pos_credit_card_installment/static/src/overrides/xml/**/*.xml',
        ],
    },
    'license': 'LGPL-3',
}
