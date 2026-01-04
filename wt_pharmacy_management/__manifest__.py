# -*- coding: utf-8 -*-
{
    'name': 'WT Pharmacy Management (Integrated)',
    'version': '18.0.6.0.0',
    'summary': 'Odoo 18 compatible backend system for managing a pharmacy.',
    'description': """
        This module provides the core functionality for managing a pharmacy by extending Odoo's native models.
        - Manages Patients and Doctors as Contacts (res.partner).
        - Manages Medicines as Products (product.template).
        - Handles Prescriptions linking patients, doctors, and medicines.
    """,
    'category': 'Industries/Healthcare',
    'author': 'Warlock Technologies Pvt Ltd.',
    'website': 'https://www.warlocktechnologies.com',
    'support': 'info@warlocktechnologies.com',
    'depends': ['base', 'product', 'sale_management', 'account', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/pharmacy_sequences.xml',
        'views/res_partner_views.xml',
        'views/product_template_views.xml',
        'views/pharmacy_prescription_views.xml',
        'views/pharmacy_menus.xml',
    ],
    'price': 00,
    'currency': 'USD',
    'images': ['static/images/screen image.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
}