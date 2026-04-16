# -*- coding: utf-8 -*-
{
    'name': 'WT Pharmacy POS (Integrated)',
    'version': '18.0.9.0.0',
    'summary': 'Odoo 18 compatible Point of Sale integration for Pharmacy.',
    'description': """
        Extends the Point of Sale interface to handle pharmacy operations.
        - Select patient (customer) at POS.
        - Load their active prescriptions into the cart.
    """,
    'category': 'Point of Sale',
    'author': 'Warlock Technologies Pvt Ltd.',
    'website': 'https://www.warlocktechnologies.com',
    'support': 'info@warlocktechnologies.com',
    'depends': ['point_of_sale', 'wt_pharmacy_management'],
    'data': [
        'views/pos_order_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            "/wt_pharmacy_pos/static/src/app/models/pos_order.js",
            "/wt_pharmacy_pos/static/src/app/control_buttons/control_buttons.js",
            "/wt_pharmacy_pos/static/src/app/control_buttons/control_buttons.xml",
        ],
    },
    'price': 00,
    'currency': 'USD',
    'images': ['static/images/screen image.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'license': 'OPL-1',
}