# -*- coding: utf-8 -*-
{
    'name': 'POS Automate Invoice | POS auto Invoice Check | POS Invoice Auto Check | Restrict POS Invoice Download',
    'summary': "Allow to auto set invoice checkbox to create invoice auto and allow to restrict invoice download.",
    'description': 'Allow to auto set invoice checkbox to create invoice auto and allow to restrict invoice download.',

    'author': 'iPredict IT Solutions Pvt. Ltd.',
    'website': 'http://ipredictitsolutions.com',
    "support": "ipredictitsolutions@gmail.com",

    'category': 'Point of Sale',
    'version': '18.0.0.1.2',
    'depends': ['point_of_sale'],

    'data': [
        'views/res_config_views.xml'

    ],

    'assets': {
        'point_of_sale._assets_pos': [
            'pos_auto_invoice_check/static/src/**/*',
        ],
    },

    'license': "OPL-1",

    'installable': True,
    'application': True,

    'images': ['static/description/banner.png'],
}
