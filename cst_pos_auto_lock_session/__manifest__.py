# -*- coding: utf-8 -*-

{
    'name': 'POS Auto Lock',
    'summary': 'Automatically lock POS after inactivity',
    'description': """
        POS Auto Lock helps protect Point of Sale sessions by automatically locking
        the POS screen after a configurable period of inactivity.

        The module monitors cashier activity such as mouse, touch, and keyboard
        interactions. If the POS remains idle for the defined time, it redirects
        to the standard Odoo POS login screen.

        The solution uses Odoo’s built-in cashier login and PIN authentication
        without altering core security behavior.

        Key Features:
        - Automatically locks POS after inactivity
        - Timeout configurable per POS configuration
        - Uses standard Odoo POS login screen
        - No impact on orders or accounting
        - Lightweight, frontend-only implementation
        
        """,
    "author": "CodeSphere Tech",
    "website": "https://www.codespheretech.in/",
    "category": "Point of Sale",
    "version": "18.0.1.0.0",
    "sequence": 0,
    "currency": "USD",
    "price": "0",
    "depends": ["point_of_sale",],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'cst_pos_auto_lock_session/static/src/js/pos_store.js',
        ],
    },
    'images': ['static/description/Banner.png'],
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "auto_install": False,
}
