# -*- coding: utf-8 -*-

{
    "name": "POS Customer Screen On Start",
    "version": "18.0.1.0.0",
    "author": "Cicindela Solutions",
    "license": "LGPL-3",
    "category": "Point of Sale",
    "website": "www.cicindelasolutions.com",
    "summary": 'Automatically opens the customer selection screen when starting the POS session',
    "description": """Automatically opens the customer selection screen at POS startup, ensuring a customer is chosen before processing orders.
""",
    "depends": ["point_of_sale"],
    "data": [
        'views/res_config_settings.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'cic_pos_customer_screen/static/src/**/*',
        ]
    },
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": False,
    "auto_install": False,
}
