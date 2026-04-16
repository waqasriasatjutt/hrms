# -*- coding: utf-8 -*-
{
    "name": "Hide Odoo Brand in User Account Menu",
    "version": "1.0",
    "category": "Web",
    "summary": "Hide Odoo branding links from top right user menu",
    "description": """
This module removes Odoo branding related links from the
top right user account menu in Odoo backend.

Hidden menu items:
- Help/Support
- My Odoo.com Account

Compatible with Odoo 18.
    """,

    "author": "Way4Tech",
    "website": "https://www.way4tech.com",
    "maintainer": "Way4Tech",
    "company": "Way4Tech",
    "license": "LGPL-3",

    "depends": ["web"],

    'data': [
        'views/login_layout.xml',
        'views/portal_record_sidebar.xml',
        'views/brand_promotion.xml',
    ],

    "assets": {
        "web.assets_backend": [
            "wt_hide_odoo/static/src/js/inherit_user_menu.js",
        ],
    },

    "installable": True,
    "application": False,
    "auto_install": False,

    "images": [
        "static/description/banner.gif",
    ],
}
