# -*- coding: utf-8 -*-
{
    'name': "POS Receipt",

    'summary': """Taxes in pos receipt orderlines""",

    'description': """
    Adds tax information in each orderline of pos receipt
    """,

    'author': "waqas riasat",
    'website': "",

    'category': 'Point of Sale',
    'version': '18.0',

    'depends': ['point_of_sale'],
    'assets': {
        'point_of_sale._assets_pos': [
            'point_of_sales_extend/static/src/**/*',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
}
