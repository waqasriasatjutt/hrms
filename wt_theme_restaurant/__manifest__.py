# -*- coding: utf-8 -*-
{
    'name': 'WT Theme Restaurant',
    'description': 'Restaurant, Cafe, Bistro, Pizzeria, Steakhouse, Fine Dining, Casual Dining, Food Truck, Bakery',
    'category': 'Theme/eCommerce',
    'summary': 'Restaurant theme: appetite-tickling hero, menu preview, chef story, reservation CTA, food gallery, testimonials, hours/location, contact. Built for restaurants, cafes, bistros, pizzerias and fine-dining brands.',
    'sequence': 320,
    'version': '19.0.1.0.0',
    'author': 'Waqas Riasat',
    'website': 'https://way4tech.com',
    'license': 'OPL-1',

    'depends': ['website'],

    'data': [
        'views/snippets/s_restaurant_hero.xml',
        'views/snippets/s_restaurant_services.xml',
        'views/snippets/s_restaurant_features.xml',
        'views/snippets/s_restaurant_showcase.xml',
        'views/snippets/s_restaurant_team.xml',
        'views/snippets/s_restaurant_testimonials.xml',
        'views/snippets/s_restaurant_faq.xml',
        'views/snippets/s_restaurant_cta.xml',
        'views/snippets/s_restaurant_contact.xml',
        'views/homepage.xml',
        'views/pages.xml',
    ],

    'assets': {
        'web._assets_primary_variables': [
            ('prepend', 'wt_theme_restaurant/static/src/scss/primary_variables.scss'),
        ],
        'web.assets_frontend': [
            'wt_theme_restaurant/static/src/scss/theme.scss',
        ],
    },

    'configurator_snippets': {
        'homepage': [
            's_restaurant_hero',
            's_restaurant_services',
            's_restaurant_features',
            's_restaurant_showcase',
            's_restaurant_team',
            's_restaurant_testimonials',
            's_restaurant_faq',
            's_restaurant_cta',
            's_restaurant_contact',
        ],
    },

    'images': ['static/description/banner.png'],
    'price': 39.0,
    'currency': 'USD',

    'installable': True,
    'application': False,
    'auto_install': False,
}
