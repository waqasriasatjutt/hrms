# -*- coding: utf-8 -*-
{
    'name': 'WT Theme Gym & Fitness',
    'description': 'Gym, Fitness, Personal Training, CrossFit, Yoga Studio, Pilates, Boxing, Martial Arts',
    'category': 'Theme/Services',
    'summary': 'Gym / fitness theme: high-energy hero, classes, trainers, membership tiers, gallery, testimonials, FAQ, contact. Built for gyms, fitness studios, CrossFit boxes, yoga studios and personal trainers.',
    'sequence': 320,
    'version': '19.0.1.0.0',
    'author': 'Waqas Riasat',
    'website': 'https://way4tech.com',
    'license': 'OPL-1',

    'depends': ['website'],

    'data': [
        'views/snippets/s_gym_hero.xml',
        'views/snippets/s_gym_services.xml',
        'views/snippets/s_gym_features.xml',
        'views/snippets/s_gym_showcase.xml',
        'views/snippets/s_gym_team.xml',
        'views/snippets/s_gym_testimonials.xml',
        'views/snippets/s_gym_faq.xml',
        'views/snippets/s_gym_cta.xml',
        'views/snippets/s_gym_contact.xml',
        'views/homepage.xml',
        'views/pages.xml',
    ],

    'assets': {
        'web._assets_primary_variables': [
            ('prepend', 'wt_theme_gym/static/src/scss/primary_variables.scss'),
        ],
        'web.assets_frontend': [
            'wt_theme_gym/static/src/scss/theme.scss',
        ],
    },

    'configurator_snippets': {
        'homepage': [
            's_gym_hero',
            's_gym_services',
            's_gym_features',
            's_gym_showcase',
            's_gym_team',
            's_gym_testimonials',
            's_gym_faq',
            's_gym_cta',
            's_gym_contact',
        ],
    },

    'images': ['static/description/banner.png'],
    'price': 39.0,
    'currency': 'USD',

    'installable': True,
    'application': False,
    'auto_install': False,
}
