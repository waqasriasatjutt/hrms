# -*- coding: utf-8 -*-

{
    'name': "Captivea POS Invoice",
    'summary': "This app is create a invoice for every POS order",
    'description': """
    Create Invoice for each and every POS order the Invoice Boolean is true by default. 
    """,
    'version': "18.0.0.1.0",
    'category': "Point of Sale",
    'depends': ['point_of_sale'],
    'author': 'Captivea',
    'maintainer': 'Captivea',
    'contributors': ["Captivea"],
    'website': 'http://www.captivea.com/',
    'assets': {
        'point_of_sale._assets_pos': [
            'cap_pos_invoice/static/src/overrides/models/pos_order.js',
        ],
    },

    'license': 'OPL-1',
    'currency': 'EUR',

    'installable': True,
    'application': False,
    'auto_install': False,
}
