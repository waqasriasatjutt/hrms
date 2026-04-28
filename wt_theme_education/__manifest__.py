# -*- coding: utf-8 -*-
{
    'name': 'WT Theme Education',
    'description': 'School, College, University, Academy, Online Course, Training Centre, Coaching, Tutoring',
    'category': 'Theme/Services',
    'summary': 'Education theme: inspiring hero, programmes, faculty, campus stats, admissions CTA, testimonials, FAQ, contact. Built for schools, colleges, universities, online-course providers and training centres.',
    'sequence': 320,
    'version': '19.0.1.0.0',
    'author': 'Waqas Riasat',
    'website': 'https://way4tech.com',
    'license': 'OPL-1',

    'depends': ['website'],

    'data': [
        'views/snippets/s_education_hero.xml',
        'views/snippets/s_education_services.xml',
        'views/snippets/s_education_features.xml',
        'views/snippets/s_education_showcase.xml',
        'views/snippets/s_education_team.xml',
        'views/snippets/s_education_testimonials.xml',
        'views/snippets/s_education_faq.xml',
        'views/snippets/s_education_cta.xml',
        'views/snippets/s_education_contact.xml',
        'views/homepage.xml',
        'views/pages.xml',
    ],

    'assets': {
        'web._assets_primary_variables': [
            ('prepend', 'wt_theme_education/static/src/scss/primary_variables.scss'),
        ],
        'web.assets_frontend': [
            'wt_theme_education/static/src/scss/theme.scss',
        ],
    },

    'configurator_snippets': {
        'homepage': [
            's_education_hero',
            's_education_services',
            's_education_features',
            's_education_showcase',
            's_education_team',
            's_education_testimonials',
            's_education_faq',
            's_education_cta',
            's_education_contact',
        ],
    },

    'images': ['static/description/banner.png'],
    'price': 39.0,
    'currency': 'USD',

    'installable': True,
    'application': False,
    'auto_install': False,
}
