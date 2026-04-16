{
    "name": "Pos Auto Send Report",
    'version': '18.0.1.0',
    'author': "Diode Info Solutions",
    'website': 'https://www.diodeinfosolutions.com/',
    'category': 'Point of Sale',
    'description': """ This module allows to send an reports through mail.""",
    "depends": ['base', 'point_of_sale', 'pos_sale'],
    'data': [

        'data/pos_report_cron.xml',
        'security/ir.model.access.csv',
        'views/pos_config.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_auto_send_report/static/src/js/send_mail.js',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
