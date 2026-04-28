# -*- coding: utf-8 -*-
{
    'name': 'WT Theme Fashion',
    'description': 'Fashion, Boutique, Apparel Brand, Designer, Atelier, Streetwear, Luxury Fashion, Couture',
    'category': 'Theme/eCommerce',
    'summary': 'Fashion theme: editorial hero, lookbook, collections, designer story, press, lookbook, contact. Built for fashion brands, boutiques, designers, ateliers and luxury labels.',
    'sequence': 320,
    'version': '19.0.1.0.0',
    'author': 'Waqas Riasat',
    'website': 'https://way4tech.com',
    'license': 'OPL-1',

    'depends': ['website'],

    'data': [
        'views/snippets/s_fashion_hero.xml',
        'views/snippets/s_fashion_services.xml',
        'views/snippets/s_fashion_features.xml',
        'views/snippets/s_fashion_showcase.xml',
        'views/snippets/s_fashion_team.xml',
        'views/snippets/s_fashion_testimonials.xml',
        'views/snippets/s_fashion_faq.xml',
        'views/snippets/s_fashion_cta.xml',
        'views/snippets/s_fashion_contact.xml',
        'views/homepage.xml',
        'views/pages.xml',
    ],

    'assets': {
        'web._assets_primary_variables': [
            ('prepend', 'wt_theme_fashion/static/src/scss/primary_variables.scss'),
        ],
        'web.assets_frontend': [
            'wt_theme_fashion/static/src/scss/theme.scss',
        ],
    },

    'configurator_snippets': {
        'homepage': [
            's_fashion_hero',
            's_fashion_services',
            's_fashion_features',
            's_fashion_showcase',
            's_fashion_team',
            's_fashion_testimonials',
            's_fashion_faq',
            's_fashion_cta',
            's_fashion_contact',
        ],
    },

    'images': ['static/description/banner.png'],
    'price': 39.0,
    'currency': 'USD',

    'installable': True,
    'application': False,
    'auto_install': False,
}
