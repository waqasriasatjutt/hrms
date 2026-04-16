# -*- coding: utf-8 -*-
{
    'name': "Odoo POS Screensaver",
    'version': '18.0.1.0',
    'category': 'Point of Sale',
    'summary': "Professional  screensaver and branding for the POS interface",
    'description': """
Adds a customizable branded screensaver to the Odoo 18 POS interface.
Admins can upload a logo/image and define an idle timeout in POS Config.
When no activity occurs for the set time, the screensaver appears automatically.
""",
    'author': "HSxTech",
    'license': 'LGPL-3',
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_config_view.xml',
    ],

    'assets': {
        'point_of_sale._assets_pos': [
            'pos_screensaver/static/src/js/screensaver.js',
            'pos_screensaver/static/src/css/screensaver.css',
        ],
    },
    "images": [
        "static/description/banner.gif",
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
