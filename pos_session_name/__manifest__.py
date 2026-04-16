# -*- coding: utf-8 -*-
{
    'name': "POS Session Name",

    'summary': "Display the POS session name directly in the Point of Sale interface.",

    'description': """ This module enhances the Point of Sale experience by displaying the active POS session name directly on the POS screen. It helps users quickly identify the currently active session, which is especially useful when multiple sessions are running across different terminals or users.""",

    'author': "Vishnu Sasikumar",
    'category': 'Point of Sale',
    'version': '18.0.3.0.0',
    'depends': ['base','point_of_sale'],

    'data': [],
    'assets': {'point_of_sale._assets_pos': [
        'pos_session_name/static/src/js/navbar_shopname.js',
        'pos_session_name/static/src/xml/navbar_shopname.xml',
        'pos_session_name/static/src/css/style.css',
    ]},
    'images': ['static/description/banner.png'],
    'license':"LGPL-3",
    'installable': True,
    'application': True,
    'auto_install': False,
}

