# Powered by Sensible Consulting Services
# -*- coding: utf-8 -*-
# © 2025 Sensible Consulting Services (<https://sensiblecs.com/>)
{
    'name': 'POS Direct Login',
    'version': '18.0.1.0',
    'summary': '''Allow direct login to POS interface without going through the backend''',
    'description': '''Sensible POS Credit Limit
        Streamline your point-of-sale experience with the Odoo POS Direct Login app. 
        This innovative tool allows businesses to bypass the traditional login steps and 
        directly access the POS system, saving valuable time and improving workflow efficiency.
    ''',
    'category': 'Sales/Point of Sale',
    'author': 'Sensible Consulting Services',
    'website': 'https://sensiblecs.com',
    'license': 'AGPL-3',
    'depends': ['point_of_sale'],
    'data': [
        'views/sbl_res_users_view.xml',
        'views/sbl_pos_order_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'sensible_pos_direct_login/static/src/**/*',
        ],
    },
    'images': ['static/description/banner.png'],
    'application': True,
    'installable': True,
}
