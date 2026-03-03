# -*- coding: utf-8 -*-
#╔══════════════════════════════════════════════════════════════════╗
#║                                                                  ║
#║                ╔═══╦╗       ╔╗  ╔╗     ╔═══╦═══╗                 ║
#║                ║╔═╗║║       ║║ ╔╝╚╗    ║╔═╗║╔═╗║                 ║
#║                ║║ ║║║╔╗╔╦╦══╣╚═╬╗╔╬╗ ╔╗║║ ╚╣╚══╗                 ║
#║                ║╚═╝║║║╚╝╠╣╔╗║╔╗║║║║║ ║║║║ ╔╬══╗║                 ║
#║                ║╔═╗║╚╣║║║║╚╝║║║║║╚╣╚═╝║║╚═╝║╚═╝║                 ║
#║                ╚╝ ╚╩═╩╩╩╩╩═╗╠╝╚╝╚═╩═╗╔╝╚═══╩═══╝                 ║
#║                          ╔═╝║     ╔═╝║                           ║
#║                          ╚══╝     ╚══╝                           ║
#║ SOFTWARE DEVELOPED AND SUPPORTED BY ALMIGHTY CONSULTING SERVICES ║
#║                   COPYRIGHT (C) 2016 - TODAY                     ║
#║                   http://www.almightycs.com                      ║
#║                                                                  ║
#╚══════════════════════════════════════════════════════════════════╝
{
    'name': 'Hospital Management System for Paediatrics ( Pediatric )',
    'version': '1.0.1',
    'summary': 'Hospital Management System for Paediatrics',
    'description': """
                Hospital Management System for Paediatrics pediatric. HealthCare Gynec system for hospitals
                With this module you can manage :
                - Child Patients
                - Maintain Child Growth Register
                - Child Vaccination
                acs hms almightycs
    """,
    'category': 'Medical',
    'author': 'Almighty Consulting Solutions Pvt. Ltd.',
    'support': 'info@almightycs.com',
    'website': 'https://www.almightycs.com',
    'license': 'OPL-1',
    'depends': ['acs_hms_vaccination'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/weight_data.xml',
        'data/height_data.xml',
        'data/head_data.xml',
        'views/acs_hms_views.xml',
        'views/hms_paediatric_view.xml',
        'views/menu_item.xml',
        'views/asset_view.xml',
    ],
    'images': [
        'static/description/hms_paediatric_almightycs_cover.jpeg',
    ],
    'installable': True,
    'application': True,
    'sequence': 1,
    'price': 101,
    'currency': 'EUR',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
