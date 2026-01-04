{
    "name": "POS Dual Currency",
    "version": "1.0",
    "summary": "Dual currency support (USD/LBP) for Odoo 18 POS",
    "description": "Adds USD/LBP toggle, conversions, and correct amounts on Payment Screen.",
    "category": "Point of Sale",
    "author": "Waqas Riasat",
    "company": "Waqas Riasat",
    "maintainer": "Waqas Riasat",
    "website": "",
    "license": "AGPL-3",
    "depends": ["pos_hr_restaurant", "point_of_sale", "custom_pos"],
    "data": [
        'views/res_config_settings.xml'
    ],
    'assets': {
            'point_of_sale._assets_pos': [

                # 'custom_dual_currency/static/src/**/*',
                'custom_dual_currency/static/src/overrides/components/apos_order.js',

                'custom_dual_currency/static/src/overrides/components/*',

                "custom_dual_currency/static/src/js/order_custom_note_patch.js",

            ],
        'point_of_sale.customer_display_assets': [
            # "custom_dual_currency/static/src/xml/customer_note.xml",
        ],
        'point_of_sale.assets_qweb': [
                # 'way4tech/custom_dual_currency/views/res_config_settings.xml',
            ]
        },
    "installable": True,
    "application": False,
    "auto_install": False,
}