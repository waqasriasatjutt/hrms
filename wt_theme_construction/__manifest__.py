# -*- coding: utf-8 -*-
{
    'name': 'WT Theme Construction',
    'description': 'Construction, Engineering, Architecture, Contractors, Builders, Civil Works, Renovation, Interior, Industrial Construction',
    'category': 'Theme/Services',
    'summary': 'Construction company theme: bold hero, services grid, project showcase, '
               'team & testimonials, contact + map. Built for builders, contractors, '
               'engineers, architects, interior designers and renovation businesses. '
               'Fully responsive, dynamic snippets, community-only — no enterprise dependency.',
    'sequence': 320,
    'version': '19.0.1.0.0',
    'author': 'Waqas Riasat',
    'website': 'https://way4tech.com',
    'license': 'OPL-1',

    'depends': ['website'],

    'data': [
        'views/snippets/s_construction_hero.xml',
        'views/snippets/s_construction_services.xml',
        'views/snippets/s_construction_features.xml',
        'views/snippets/s_construction_projects.xml',
        'views/snippets/s_construction_stats.xml',
        'views/snippets/s_construction_team.xml',
        'views/snippets/s_construction_testimonials.xml',
        'views/snippets/s_construction_cta.xml',
        'views/snippets/s_construction_contact.xml',
        'views/homepage.xml',
        'views/pages.xml',
    ],

    'assets': {
        'web._assets_primary_variables': [
            ('prepend', 'wt_theme_construction/static/src/scss/primary_variables.scss'),
        ],
        'web.assets_frontend': [
            'wt_theme_construction/static/src/scss/theme.scss',
        ],
    },

    # When the user picks this theme in the website configurator, lay these
    # snippets out on the homepage in this order.
    'configurator_snippets': {
        'homepage': [
            's_construction_hero',
            's_construction_services',
            's_construction_features',
            's_construction_projects',
            's_construction_stats',
            's_construction_team',
            's_construction_testimonials',
            's_construction_cta',
            's_construction_contact',
        ],
    },

    'images': ['static/description/banner.png'],
    'price': 39.0,
    'currency': 'USD',

    'installable': True,
    'application': False,
    'auto_install': False,
}
