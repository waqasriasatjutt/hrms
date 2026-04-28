# -*- coding: utf-8 -*-
{
    'name': 'WT Theme NGO & Nonprofit',
    'description': 'NGO, Nonprofit, Charity, Foundation, Social Enterprise, Volunteer Organization, Cause',
    'category': 'Theme/Services',
    'summary': 'NGO / nonprofit theme: mission hero, programmes, impact stats, donation CTA, volunteers, testimonials, FAQ, contact. Built for charities, foundations, NGOs, social enterprises and volunteer organisations.',
    'sequence': 320,
    'version': '19.0.1.0.0',
    'author': 'Waqas Riasat',
    'website': 'https://way4tech.com',
    'license': 'OPL-1',

    'depends': ['website'],

    'data': [
        'views/snippets/s_ngo_hero.xml',
        'views/snippets/s_ngo_services.xml',
        'views/snippets/s_ngo_features.xml',
        'views/snippets/s_ngo_showcase.xml',
        'views/snippets/s_ngo_team.xml',
        'views/snippets/s_ngo_testimonials.xml',
        'views/snippets/s_ngo_faq.xml',
        'views/snippets/s_ngo_cta.xml',
        'views/snippets/s_ngo_contact.xml',
        'views/homepage.xml',
        'views/pages.xml',
    ],

    'assets': {
        'web._assets_primary_variables': [
            ('prepend', 'wt_theme_ngo/static/src/scss/primary_variables.scss'),
        ],
        'web.assets_frontend': [
            'wt_theme_ngo/static/src/scss/theme.scss',
        ],
    },

    'configurator_snippets': {
        'homepage': [
            's_ngo_hero',
            's_ngo_services',
            's_ngo_features',
            's_ngo_showcase',
            's_ngo_team',
            's_ngo_testimonials',
            's_ngo_faq',
            's_ngo_cta',
            's_ngo_contact',
        ],
    },

    'images': ['static/description/banner.png'],
    'price': 39.0,
    'currency': 'USD',

    'installable': True,
    'application': False,
    'auto_install': False,
}
