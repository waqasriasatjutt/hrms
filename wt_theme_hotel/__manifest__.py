# -*- coding: utf-8 -*-
{
    'name': 'WT Theme Hotel',
    'description': 'Hotel, Resort, Boutique Hotel, Bed & Breakfast, Lodge, Villa, Vacation Rental',
    'category': 'Theme/Services',
    'summary': 'Hotel theme: cinematic hero, room types, amenities, gallery, booking widget, reviews, location, contact. Built for hotels, resorts, boutique hotels, B&Bs, lodges and vacation rentals.',
    'sequence': 320,
    'version': '19.0.1.0.0',
    'author': 'Waqas Riasat',
    'website': 'https://way4tech.com',
    'license': 'OPL-1',

    'depends': ['website'],

    'data': [
        'views/snippets/s_hotel_hero.xml',
        'views/snippets/s_hotel_services.xml',
        'views/snippets/s_hotel_features.xml',
        'views/snippets/s_hotel_showcase.xml',
        'views/snippets/s_hotel_team.xml',
        'views/snippets/s_hotel_testimonials.xml',
        'views/snippets/s_hotel_faq.xml',
        'views/snippets/s_hotel_cta.xml',
        'views/snippets/s_hotel_contact.xml',
        'views/homepage.xml',
        'views/pages.xml',
    ],

    'assets': {
        'web._assets_primary_variables': [
            ('prepend', 'wt_theme_hotel/static/src/scss/primary_variables.scss'),
        ],
        'web.assets_frontend': [
            'wt_theme_hotel/static/src/scss/theme.scss',
        ],
    },

    'configurator_snippets': {
        'homepage': [
            's_hotel_hero',
            's_hotel_services',
            's_hotel_features',
            's_hotel_showcase',
            's_hotel_team',
            's_hotel_testimonials',
            's_hotel_faq',
            's_hotel_cta',
            's_hotel_contact',
        ],
    },

    'images': ['static/description/banner.png'],
    'price': 39.0,
    'currency': 'USD',

    'installable': True,
    'application': False,
    'auto_install': False,
}
