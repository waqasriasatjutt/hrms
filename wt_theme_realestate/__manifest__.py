# -*- coding: utf-8 -*-
{
    'name': 'WT Theme Real Estate',
    'description': 'Real Estate, Property, Real Estate Agency, Brokers, Listings, Apartments, Houses, Commercial Property',
    'category': 'Theme/Services',
    'summary': 'Real estate theme: hero with property search, featured listings, agent grid, why-us, mortgage CTA, testimonials, contact. Built for real-estate agencies, brokers, developers and property managers.',
    'sequence': 320,
    'version': '19.0.1.0.0',
    'author': 'Waqas Riasat',
    'website': 'https://way4tech.com',
    'license': 'OPL-1',

    'depends': ['website'],

    'data': [
        'views/snippets/s_realestate_hero.xml',
        'views/snippets/s_realestate_services.xml',
        'views/snippets/s_realestate_features.xml',
        'views/snippets/s_realestate_showcase.xml',
        'views/snippets/s_realestate_team.xml',
        'views/snippets/s_realestate_testimonials.xml',
        'views/snippets/s_realestate_faq.xml',
        'views/snippets/s_realestate_cta.xml',
        'views/snippets/s_realestate_contact.xml',
        'views/homepage.xml',
        'views/pages.xml',
    ],

    'assets': {
        'web._assets_primary_variables': [
            ('prepend', 'wt_theme_realestate/static/src/scss/primary_variables.scss'),
        ],
        'web.assets_frontend': [
            'wt_theme_realestate/static/src/scss/theme.scss',
        ],
    },

    'configurator_snippets': {
        'homepage': [
            's_realestate_hero',
            's_realestate_services',
            's_realestate_features',
            's_realestate_showcase',
            's_realestate_team',
            's_realestate_testimonials',
            's_realestate_faq',
            's_realestate_cta',
            's_realestate_contact',
        ],
    },

    'images': ['static/description/banner.png'],
    'price': 39.0,
    'currency': 'USD',

    'installable': True,
    'application': False,
    'auto_install': False,
}
