# -*- coding: utf-8 -*-
{
    'name': 'Pos Survey',
    'version': '18.0.1.0',
    'category': 'Sales/Point of Sale',
    'summary': '''
        Take quick surveys in POS
    ''',
    'description': """
    """,
    'depends': ['pos_hr', 'survey'],
    'website': '',
    'author': 'Z-Sync',
    'demo':[
        'data/demo_data.xml',
    ],
    'data': [
        'security/security.xml',
        'views/survey_survey_views.xml',
        'views/survey_question_views.xml',
        'views/survey_user_input_views.xml',
        'views/pos_order_views.xml',
        'views/pos_session_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'price': 0.0,
    'currency': 'USD',
    'images': [
        'static/description/main_screenshot.png',
    ],
    'installable': True,
    'application': False,
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_survey/static/src/app/**/*',
        ],
    },
    'license': 'OPL-1',
}
