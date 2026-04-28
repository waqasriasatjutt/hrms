# -*- coding: utf-8 -*-
{
    'name': 'WT Theme eCommerce',
    'description': 'eCommerce, Online Shop, Online Store, Multi-Brand Store, Boutique, Marketplace, Retail',
    'category': 'Theme/eCommerce',
    'summary': 'eCommerce theme: brand-forward hero, category cards, featured products, why-us, reviews, newsletter, contact. Built for online stores, boutiques, multi-brand shops and retail brands. Optional website_sale integration.',
    'sequence': 320,
    'version': '19.0.1.0.0',
    'author': 'Waqas Riasat',
    'website': 'https://way4tech.com',
    'license': 'OPL-1',

    'depends': ['website'],

    'data': [
        'views/snippets/s_ecommerce_hero.xml',
        'views/snippets/s_ecommerce_services.xml',
        'views/snippets/s_ecommerce_features.xml',
        'views/snippets/s_ecommerce_showcase.xml',
        'views/snippets/s_ecommerce_team.xml',
        'views/snippets/s_ecommerce_testimonials.xml',
        'views/snippets/s_ecommerce_faq.xml',
        'views/snippets/s_ecommerce_cta.xml',
        'views/snippets/s_ecommerce_contact.xml',
        'views/homepage.xml',
        'views/pages.xml',
    ],

    'assets': {
        'web._assets_primary_variables': [
            ('prepend', 'wt_theme_ecommerce/static/src/scss/primary_variables.scss'),
        ],
        'web.assets_frontend': [
            'wt_theme_ecommerce/static/src/scss/theme.scss',
        ],
    },

    'configurator_snippets': {
        'homepage': [
            's_ecommerce_hero',
            's_ecommerce_services',
            's_ecommerce_features',
            's_ecommerce_showcase',
            's_ecommerce_team',
            's_ecommerce_testimonials',
            's_ecommerce_faq',
            's_ecommerce_cta',
            's_ecommerce_contact',
        ],
    },

    'images': ['static/description/banner.png'],
    'price': 39.0,
    'currency': 'USD',

    'installable': True,
    'application': False,
    'auto_install': False,
}
