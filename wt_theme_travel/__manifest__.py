# -*- coding: utf-8 -*-
{
    'name': 'WT Theme Travel & Tours',
    'description': 'Travel Agency, Tour Operator, Vacation, Holidays, Adventure Travel, Cruises, Honeymoon, Safari',
    'category': 'Theme/Services',
    'summary': 'Travel theme: wanderlust hero, destinations, packages, why-us, gallery, testimonials, contact. Built for travel agencies, tour operators, adventure-travel and honeymoon specialists.',
    'sequence': 320,
    'version': '19.0.1.0.0',
    'author': 'Waqas Riasat',
    'website': 'https://way4tech.com',
    'license': 'OPL-1',

    'depends': ['website'],

    'data': [
        'views/snippets/s_travel_hero.xml',
        'views/snippets/s_travel_services.xml',
        'views/snippets/s_travel_features.xml',
        'views/snippets/s_travel_showcase.xml',
        'views/snippets/s_travel_team.xml',
        'views/snippets/s_travel_testimonials.xml',
        'views/snippets/s_travel_faq.xml',
        'views/snippets/s_travel_cta.xml',
        'views/snippets/s_travel_contact.xml',
        'views/homepage.xml',
        'views/pages.xml',
    ],

    'assets': {
        'web._assets_primary_variables': [
            ('prepend', 'wt_theme_travel/static/src/scss/primary_variables.scss'),
        ],
        'web.assets_frontend': [
            'wt_theme_travel/static/src/scss/theme.scss',
        ],
    },

    'configurator_snippets': {
        'homepage': [
            's_travel_hero',
            's_travel_services',
            's_travel_features',
            's_travel_showcase',
            's_travel_team',
            's_travel_testimonials',
            's_travel_faq',
            's_travel_cta',
            's_travel_contact',
        ],
    },

    'images': ['static/description/banner.png'],
    'price': 39.0,
    'currency': 'USD',

    'installable': True,
    'application': False,
    'auto_install': False,
}
