# -*- coding: utf-8 -*-
{
    'name': 'WT Theme Consulting',
    'description': 'Consulting, Agency, Strategy, Business Consulting, Digital Agency, Creative Agency, Marketing',
    'category': 'Theme/Services',
    'summary': 'Consulting / agency theme: confident hero, services, case studies, methodology, team, testimonials, contact. Built for consulting firms, agencies, strategy practices and creative shops.',
    'sequence': 320,
    'version': '19.0.1.0.0',
    'author': 'Waqas Riasat',
    'website': 'https://way4tech.com',
    'license': 'OPL-1',

    'depends': ['website'],

    'data': [
        'views/snippets/s_consulting_hero.xml',
        'views/snippets/s_consulting_services.xml',
        'views/snippets/s_consulting_features.xml',
        'views/snippets/s_consulting_showcase.xml',
        'views/snippets/s_consulting_team.xml',
        'views/snippets/s_consulting_testimonials.xml',
        'views/snippets/s_consulting_faq.xml',
        'views/snippets/s_consulting_cta.xml',
        'views/snippets/s_consulting_contact.xml',
        'views/homepage.xml',
        'views/pages.xml',
    ],

    'assets': {
        'web._assets_primary_variables': [
            ('prepend', 'wt_theme_consulting/static/src/scss/primary_variables.scss'),
        ],
        'web.assets_frontend': [
            'wt_theme_consulting/static/src/scss/theme.scss',
        ],
    },

    'configurator_snippets': {
        'homepage': [
            's_consulting_hero',
            's_consulting_services',
            's_consulting_features',
            's_consulting_showcase',
            's_consulting_team',
            's_consulting_testimonials',
            's_consulting_faq',
            's_consulting_cta',
            's_consulting_contact',
        ],
    },

    'images': ['static/description/banner.png'],
    'price': 39.0,
    'currency': 'USD',

    'installable': True,
    'application': False,
    'auto_install': False,
}
