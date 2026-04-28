# -*- coding: utf-8 -*-
{
    'name': 'WT Theme SaaS Startup',
    'description': 'SaaS, Software, Tech Startup, Product Landing, Cloud Platform, B2B Tool, Developer Tools',
    'category': 'Theme/Services',
    'summary': 'SaaS / startup theme: product-focused hero, features, pricing tiers, integrations, customer logos, testimonials, FAQ, contact. Built for SaaS companies, software products, tech startups and B2B tools.',
    'sequence': 320,
    'version': '19.0.1.0.0',
    'author': 'Waqas Riasat',
    'website': 'https://way4tech.com',
    'license': 'OPL-1',

    'depends': ['website'],

    'data': [
        'views/snippets/s_saas_hero.xml',
        'views/snippets/s_saas_services.xml',
        'views/snippets/s_saas_features.xml',
        'views/snippets/s_saas_showcase.xml',
        'views/snippets/s_saas_team.xml',
        'views/snippets/s_saas_testimonials.xml',
        'views/snippets/s_saas_faq.xml',
        'views/snippets/s_saas_cta.xml',
        'views/snippets/s_saas_contact.xml',
        'views/homepage.xml',
        'views/pages.xml',
    ],

    'assets': {
        'web._assets_primary_variables': [
            ('prepend', 'wt_theme_saas/static/src/scss/primary_variables.scss'),
        ],
        'web.assets_frontend': [
            'wt_theme_saas/static/src/scss/theme.scss',
        ],
    },

    'configurator_snippets': {
        'homepage': [
            's_saas_hero',
            's_saas_services',
            's_saas_features',
            's_saas_showcase',
            's_saas_team',
            's_saas_testimonials',
            's_saas_faq',
            's_saas_cta',
            's_saas_contact',
        ],
    },

    'images': ['static/description/banner.png'],
    'price': 39.0,
    'currency': 'USD',

    'installable': True,
    'application': False,
    'auto_install': False,
}
