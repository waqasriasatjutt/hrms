# -*- coding: utf-8 -*-
{
    'name': 'WT Theme Law Firm',
    'description': 'Law Firm, Legal Consultancy, Advocates, Solicitors, Notaries, Corporate Law, Litigation, Tax Law',
    'category': 'Theme/Services',
    'summary': 'Law firm theme: authoritative hero, practice areas, partners, case-results stats, free-consultation CTA, testimonials, FAQ, contact. Built for advocates, solicitors, notaries and corporate-law practices.',
    'sequence': 320,
    'version': '19.0.1.0.0',
    'author': 'Waqas Riasat',
    'website': 'https://way4tech.com',
    'license': 'OPL-1',

    'depends': ['website'],

    'data': [
        'views/snippets/s_lawfirm_hero.xml',
        'views/snippets/s_lawfirm_services.xml',
        'views/snippets/s_lawfirm_features.xml',
        'views/snippets/s_lawfirm_showcase.xml',
        'views/snippets/s_lawfirm_team.xml',
        'views/snippets/s_lawfirm_testimonials.xml',
        'views/snippets/s_lawfirm_faq.xml',
        'views/snippets/s_lawfirm_cta.xml',
        'views/snippets/s_lawfirm_contact.xml',
        'views/homepage.xml',
        'views/pages.xml',
    ],

    'assets': {
        'web._assets_primary_variables': [
            ('prepend', 'wt_theme_lawfirm/static/src/scss/primary_variables.scss'),
        ],
        'web.assets_frontend': [
            'wt_theme_lawfirm/static/src/scss/theme.scss',
        ],
    },

    'configurator_snippets': {
        'homepage': [
            's_lawfirm_hero',
            's_lawfirm_services',
            's_lawfirm_features',
            's_lawfirm_showcase',
            's_lawfirm_team',
            's_lawfirm_testimonials',
            's_lawfirm_faq',
            's_lawfirm_cta',
            's_lawfirm_contact',
        ],
    },

    'images': ['static/description/banner.png'],
    'price': 39.0,
    'currency': 'USD',

    'installable': True,
    'application': False,
    'auto_install': False,
}
