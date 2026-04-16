{
    'name': "ICS POS Receipt NearPay",
    "version": "18.0.1.0.0",
    "category": "Point of Sale",
    "summary": "Display NearPay transaction details in POS receipt",
    "description": """Adds NearPay payment info to the standard POS receipt. the module depend on ics_pos_nearpay_integration module """,
    'author': 'iCloud Solutions',
    'website': "https://icloud-solutions.net",
    'company': 'iCloud Solutions',
    'maintainer': 'iCloud Solutions',
    'depends': ['point_of_sale'],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'ics_pos_receipt_nearpay/static/src/xml/OrderReceipt.xml',
            'ics_pos_receipt_nearpay/static/src/js/PosOrder.js',
        ]
    },
    "images": ["static/description/img/thumbnail.png","static/description/icon.png", "static/description/banner.png"],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': '0',
    'currency': 'EUR'
}
