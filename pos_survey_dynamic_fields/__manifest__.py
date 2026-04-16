# -*- coding: utf-8 -*-
{
    'name': 'Dynamic Fields for Pos Survey',
    'version': '18.0.1.0',
    'category': 'Sales/Point of Sale',
    'summary': '''
        This module enables dynamic survey questions with answers based on system parameters.
    ''',
    'description': """
    """,
    'depends': ['pos_survey'],
    'website': '',
    'author': 'Z-Sync',
    'data': [
        'views/survey_question_views.xml'
    ],
    'installable': True,
    'application': False,
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_survey_dynamic_fields/static/src/app/store/**/*',
        ],
    },
    'license': 'OPL-1',
}
