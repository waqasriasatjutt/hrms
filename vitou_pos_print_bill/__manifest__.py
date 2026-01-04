# -*- coding: utf-8 -*-
{
    'name': "POS Print Bill Button",
    'author': 'V Technologies',
    'website': 'https://apps.odoo.com/apps/modules/browse?search=vitou',
    'maintainer': 'V Technologies',
    'version': '18.0.0.1',
    'category': 'Point of Sale',
    'sequence': 75,
    'summary': 'POS Print Bill Button Near Action Button, odoo bill button',
    #'price':'10.0',
    #'currency':'USD',
    # 'description': "Display Sale Price in POS",
    'depends': [
        'base',
        'point_of_sale',
        # 'hr.employee',

    ],
    'data': [
        # 'security/security.xml',
        # 'security/ir.model.access.csv',

    ],

    'assets': {
        'point_of_sale._assets_pos': [

            'vitou_pos_print_bill/static/src/js/pos_print_bill_button.js',
            'vitou_pos_print_bill/static/src/xml/pos_print_bill_button.xml',

        ],

    },

    # "qweb": ["vitou_pos_print_slip/static/src/xml/pos.xml"],

    'images': ['static/description/banner.png'],
    "installable": True,
    "application": True,
    "auto_install": False,
    'license': 'OPL-1',
}
