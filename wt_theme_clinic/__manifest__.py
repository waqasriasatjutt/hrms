# -*- coding: utf-8 -*-
{
    'name': 'WT Theme Clinic',
    'description': 'Medical Clinic, Hospital, Dental, Pediatric, Cardiology, Dermatology, Veterinary, Aesthetic, Chiropractic, Physiotherapy',
    'category': 'Theme/Services',
    'summary': 'Healthcare theme: trust-first hero, services by speciality, doctor team, '
               'patient testimonials, online appointment CTA, contact + map. Built for '
               'clinics, hospitals, dental practices, vet clinics, physiotherapy centres '
               'and aesthetic medicine. Fully responsive, dynamic snippets, community-only.',
    'sequence': 320,
    'version': '19.0.1.0.0',
    'author': 'Waqas Riasat',
    'website': 'https://way4tech.com',
    'license': 'OPL-1',

    'depends': ['website'],

    'data': [
        'views/snippets/s_clinic_hero.xml',
        'views/snippets/s_clinic_services.xml',
        'views/snippets/s_clinic_features.xml',
        'views/snippets/s_clinic_doctors.xml',
        'views/snippets/s_clinic_appointment.xml',
        'views/snippets/s_clinic_stats.xml',
        'views/snippets/s_clinic_testimonials.xml',
        'views/snippets/s_clinic_faq.xml',
        'views/snippets/s_clinic_contact.xml',
        'views/homepage.xml',
        'views/pages.xml',
    ],

    'assets': {
        'web._assets_primary_variables': [
            ('prepend', 'wt_theme_clinic/static/src/scss/primary_variables.scss'),
        ],
        'web.assets_frontend': [
            'wt_theme_clinic/static/src/scss/theme.scss',
        ],
    },

    'configurator_snippets': {
        'homepage': [
            's_clinic_hero',
            's_clinic_services',
            's_clinic_features',
            's_clinic_doctors',
            's_clinic_stats',
            's_clinic_appointment',
            's_clinic_testimonials',
            's_clinic_faq',
            's_clinic_contact',
        ],
    },

    'images': ['static/description/banner.png'],
    'price': 39.0,
    'currency': 'USD',

    'installable': True,
    'application': False,
    'auto_install': False,
}
