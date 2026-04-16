# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Point of Sale Subtotal To Qty',
    'version': '1.0',
    'category': 'Sales/Point of Sale',
    'sequence': 6,
    'summary': 'Add total amount convert to qty ',
    'description': """
    Add total amount convert to qty based on the product
    Especially for Petrol Station.

""",
    'author': "MYAT THU",
    'depends': ['point_of_sale'],
    'data': [
        'views/product_product_view.xml'
    ],
    'installable': True,
    'assets': {
        'point_of_sale._assets_pos': [
            'mt_pos_subtotal_to_qty/static/src/**/*',
        ],
    },
    'images': ['static/description/images/sample-pos-setsubtotal.png'],
    'license': 'LGPL-3',
}
