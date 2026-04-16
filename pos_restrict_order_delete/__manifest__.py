# -*- coding: utf-8 -*-
{
    'name': 'POS Restrict Order Delete',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Remove Delete Button from POS Ticket Screen',
    'description': """
        POS Restrict Order Delete
        =========================
        
        This module hides the "Delete Order" (Trash Icon) button from the POS Ticket Screen (Orders List).
        This prevents users from deleting orders directly from the POS interface.
    """,
    'author': 'NEXERP PRIVATE LIMITED',
    'website': 'https://nexeerp.com',
    'license': 'LGPL-3',
    'depends': ['point_of_sale', 'pos_restaurant'],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_restrict_order_delete/static/src/js/ticket_screen_extension.js',
            'pos_restrict_order_delete/static/src/js/pos_store_extension.js',
            'pos_restrict_order_delete/static/src/js/order_summary_extension.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'images': ['static/description/banner.png'],
}
