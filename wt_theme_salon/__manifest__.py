# -*- coding: utf-8 -*-
{
    'name': 'WT Theme Salon & Spa',
    'description': 'Salon, Spa, Beauty, Hair Salon, Nail Salon, Barbershop, Aesthetic Studio, Wellness Centre',
    'category': 'Theme/Services',
    'summary': 'Salon / spa theme: aspirational hero, services menu, stylists, booking CTA, gallery, testimonials, FAQ, contact. Built for salons, spas, barbers, nail studios, wellness centres and aesthetic clinics.',
    'sequence': 320,
    'version': '19.0.1.0.0',
    'author': 'Waqas Riasat',
    'website': 'https://way4tech.com',
    'license': 'OPL-1',

    'depends': ['website'],

    'data': [
        'views/snippets/s_salon_hero.xml',
        'views/snippets/s_salon_services.xml',
        'views/snippets/s_salon_features.xml',
        'views/snippets/s_salon_showcase.xml',
        'views/snippets/s_salon_team.xml',
        'views/snippets/s_salon_testimonials.xml',
        'views/snippets/s_salon_faq.xml',
        'views/snippets/s_salon_cta.xml',
        'views/snippets/s_salon_contact.xml',
        'views/homepage.xml',
        'views/pages.xml',
    ],

    'assets': {
        'web._assets_primary_variables': [
            ('prepend', 'wt_theme_salon/static/src/scss/primary_variables.scss'),
        ],
        'web.assets_frontend': [
            'wt_theme_salon/static/src/scss/theme.scss',
        ],
    },

    'configurator_snippets': {
        'homepage': [
            's_salon_hero',
            's_salon_services',
            's_salon_features',
            's_salon_showcase',
            's_salon_team',
            's_salon_testimonials',
            's_salon_faq',
            's_salon_cta',
            's_salon_contact',
        ],
    },

    'images': ['static/description/banner.png'],
    'price': 39.0,
    'currency': 'USD',

    'installable': True,
    'application': False,
    'auto_install': False,
}
