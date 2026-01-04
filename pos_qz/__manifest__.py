{
    "name": "POS QZ Print Silent",
    "version": "0.1",
    "summary": "POS Customisaion",
    "description": "Print via qz tray silent print.",
    "category": "Point of Sale",
    "author": "Waqas Riasat",
    "company": "Waqas Riasat",
    "maintainer": "Waqas Riasat",
    "website": "",
    "license": "AGPL-3",
    "depends": ["pos_hr_restaurant","point_of_sale"],
    "data": [
        'security/ir.model.access.csv',
        # 'views/note_view.xml',
        'views/res_config_settings.xml',
        'views/pos_printer.xml'
    ],
    'assets': {
            'point_of_sale._assets_pos': [
                'pos_qz/static/src/**/*',
                # "pos_qz/static/src/xml/customer_navbar_template.xml",

            ],
        'point_of_sale.customer_display_assets': [
            # "custom_pos/static/src/xml/customer_note.xml",
        ],
        'point_of_sale.assets_qweb': [
                # 'way4tech/custom_pos/views/res_config_settings.xml',
            ]
        },
    "installable": True,
    "application": False,
    "auto_install": False,
}