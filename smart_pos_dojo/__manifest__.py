# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Dojo Payments POS',
    'version': '18.0.0.1',
    "author": "Smart IT Ltd",
    'category': 'Sales/Point Of Sale',
    'maintainer': "Smart IT Ltd",
    'website': 'https://smart-ltd.co.uk',
    'summary': 'Dojo Integration for Odoo',
    'description': """Integrate Dojo card terminals with Odoo Point of Sale.

                This module enables seamless integration between Dojo payment terminals and Odoo POS, allowing businesses to take card payments directly from within the POS interface.

                Key Features:

                    - Direct integration with Dojo terminals (via API)
                    - Supports card, contactless, and mobile wallet payments
                    - Automatically sends payment amount from Odoo to the terminal
                    - Records successful payments against the POS order
                    - Compatible with multi-terminal and multi-session setups
                    - Quick setup with support for Dojo account onboarding

                Ideal for UK businesses using Dojo for face-to-face payments.

                Note: Requires an active Dojo account and compatible terminal.""",
    'data': [
        'security/ir.model.access.csv',
        'views/pos_payment_method_views.xml',
        'views/res_company_views.xml',
        'views/res_config_views.xml',
        'views/pos_order_view.xml',
        'data/cron.xml',
    ],
    'depends': ['point_of_sale'],
    'installable': True,
    'auto_install': False,
    'assets': {
        'point_of_sale._assets_pos': [
            'smart_pos_dojo/static/**/*',
        ],
    },
    'license': 'OPL-1',
    'support': 'productsupport@smart-ltd.co.uk',
    'images':['static/description/images/cover-image.png']
}
