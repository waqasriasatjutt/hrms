# -*- coding: utf-8 -*-
{
    'name': 'WT Theme Photography',
    'description': 'Photography, Portfolio, Photographer, Studio, Wedding Photography, Portrait, Commercial Photography',
    'category': 'Theme/Creative',
    'summary': 'Photography theme: minimalist hero, portfolio grid, services, about, packages, testimonials, contact. Built for photographers, studios, wedding/portrait photographers and visual artists.',
    'sequence': 320,
    'version': '19.0.1.0.0',
    'author': 'Waqas Riasat',
    'website': 'https://way4tech.com',
    'license': 'OPL-1',

    'depends': ['website'],

    'data': [
        'views/snippets/s_photography_hero.xml',
        'views/snippets/s_photography_services.xml',
        'views/snippets/s_photography_features.xml',
        'views/snippets/s_photography_showcase.xml',
        'views/snippets/s_photography_team.xml',
        'views/snippets/s_photography_testimonials.xml',
        'views/snippets/s_photography_faq.xml',
        'views/snippets/s_photography_cta.xml',
        'views/snippets/s_photography_contact.xml',
        'views/homepage.xml',
        'views/pages.xml',
    ],

    'assets': {
        'web._assets_primary_variables': [
            ('prepend', 'wt_theme_photography/static/src/scss/primary_variables.scss'),
        ],
        'web.assets_frontend': [
            'wt_theme_photography/static/src/scss/theme.scss',
        ],
    },

    'configurator_snippets': {
        'homepage': [
            's_photography_hero',
            's_photography_services',
            's_photography_features',
            's_photography_showcase',
            's_photography_team',
            's_photography_testimonials',
            's_photography_faq',
            's_photography_cta',
            's_photography_contact',
        ],
    },

    'images': ['static/description/banner.png'],
    'price': 39.0,
    'currency': 'USD',

    'installable': True,
    'application': False,
    'auto_install': False,
}
