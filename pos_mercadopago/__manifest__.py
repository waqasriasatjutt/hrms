# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Pos MP Base",
    "summary": """
        Integrate your POS with a Mp
    """,
    "description": """
Allow to pay with MP
==============================

This module allows customers to pay for their orders with credit
cards. The transactions are processed by MP (developed by Axcelere). 
    """,
    "author": "Axcelere",
    "website": "https://www.axcelere.com",
    "category": "Sales/Point of Sale",
    "version": "18.0.0.0",
    "depends": [
        "point_of_sale",
    ],

    'data': [
        'security/ir.model.access.csv',
        'data/cron_jobs.xml',
        'views/mp_credential_views.xml',
        'views/mp_store_views.xml',
        'views/mp_store_box_views.xml',
        # 'views/pos_payment_method_views.xml',
        'views/mp_log_views.xml',
        'views/mp_notification_views.xml',
    ],
    "installable": True,
    "license": "GPL-3",
}
