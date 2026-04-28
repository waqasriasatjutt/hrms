# -*- coding: utf-8 -*-
{
    'name': 'WT Theme Events',
    'description': 'Event, Conference, Festival, Summit, Wedding, Corporate Event, Concert, Workshop',
    'category': 'Theme/Services',
    'summary': 'Event theme: countdown hero, schedule, speakers, sponsors, tickets CTA, gallery, FAQ, contact. Built for conferences, festivals, summits, weddings and corporate events.',
    'sequence': 320,
    'version': '19.0.1.0.0',
    'author': 'Waqas Riasat',
    'website': 'https://way4tech.com',
    'license': 'OPL-1',

    'depends': ['website'],

    'data': [
        'views/snippets/s_event_hero.xml',
        'views/snippets/s_event_services.xml',
        'views/snippets/s_event_features.xml',
        'views/snippets/s_event_showcase.xml',
        'views/snippets/s_event_team.xml',
        'views/snippets/s_event_testimonials.xml',
        'views/snippets/s_event_faq.xml',
        'views/snippets/s_event_cta.xml',
        'views/snippets/s_event_contact.xml',
        'views/homepage.xml',
        'views/pages.xml',
    ],

    'assets': {
        'web._assets_primary_variables': [
            ('prepend', 'wt_theme_event/static/src/scss/primary_variables.scss'),
        ],
        'web.assets_frontend': [
            'wt_theme_event/static/src/scss/theme.scss',
        ],
    },

    'configurator_snippets': {
        'homepage': [
            's_event_hero',
            's_event_services',
            's_event_features',
            's_event_showcase',
            's_event_team',
            's_event_testimonials',
            's_event_faq',
            's_event_cta',
            's_event_contact',
        ],
    },

    'images': ['static/description/banner.png'],
    'price': 39.0,
    'currency': 'USD',

    'installable': True,
    'application': False,
    'auto_install': False,
}
