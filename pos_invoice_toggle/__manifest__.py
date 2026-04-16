# -*- coding: utf-8 -*-
{
    "name": "POS Invoice Toggle",
    'summary': "Toggle Invoice Button in POS with a Single Click!.",

    'description': """

            Easily control the visibility of the Invoice button in POS. With this module, you can hide or show the button directly from POS configuration settings.

    """,
    'author': "Apurva Wanjari",
    'license': 'LGPL-3',
    'category': 'point of sale',
    'website': 'https://apps.odoo.com/apps/modules/browse?search=apurva+wanjari',
    "version": "17.0",
    "depends": ["point_of_sale"],
    "data": [
        "views/res_config_settings_views.xml",
    ],

    'assets': {
        'point_of_sale._assets_pos': [
            "pos_invoice_toggle/static/src/js/invoice_button.js", 
        ],
    },
        "images": ["static/description/banner.png"],
        "installable": True,
        "application": False,
        "auto_install": False,
        
    }

