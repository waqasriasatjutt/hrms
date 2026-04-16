# -*- coding: utf-8 -*-


{
    'name': 'Rewards Codes',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'summary': 'Reward your customers for their loyalty',
    'description': """
        - Rewarding a customer after an order has been processed
    """,
    'depends': ['point_of_sale'],
    'author': 'Rewards Codes',
    'maintainer': 'Rewards Codes',
    'company': 'Rewards Codes',
    'website': 'https://rewards.codes/',
    'assets': {
        'point_of_sale._assets_pos': [
            '/rewards_codes/static/src/**/*',
        ],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/pos_rewards_views.xml',
    ],
    # 'qweb': [
    #     'static/src/xml/custom_button.xml',
    # ],
    'images': ['static/description/banner.png'],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
