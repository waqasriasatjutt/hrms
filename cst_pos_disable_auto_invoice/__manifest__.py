# -*- coding: utf-8 -*-

{
    'name': 'POS Invoice Auto Enable | Restrict PDF Download',
    'summary': 'Automatically check the Invoice option in POS and restrict the automatic download of invoice PDFs.',
    'description': """
        This module enhances the Point of Sale workflow by automatically enabling the Invoice option
        and restricting the automatic download of PDF invoices from the POS interface.

        It is designed for businesses that want better control over invoice handling in POS,
        avoiding unnecessary or unauthorized invoice PDF downloads while ensuring that orders
        are properly invoiced.

        Key Features:
        • Automatically enables the Invoice option in POS
        • Prevents automatic PDF invoice download after order validation
        • Helps control invoice access and reduce unwanted file downloads
        • Seamless integration with Odoo Point of Sale
        • No impact on standard POS billing or accounting flow
    """,
    "author": "CodeSphere Tech",
    "website": "https://www.codespheretech.in/",
    "category": "Point of Sale",
    "version": "18.0.1.0.0",
    "sequence": 0,
    "currency": "USD",
    "price": "0",
    "depends": ["account", "point_of_sale", ],
    "data": [
        'views/res_config_views.xml',
    ],
    "assets": {
        'point_of_sale._assets_pos': [
            'cst_pos_disable_auto_invoice/static/src/**/*',
        ],
    },
    "images": ["static/description/Banner.png"],
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "auto_install": False,
}
