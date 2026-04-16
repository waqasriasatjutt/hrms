# -*- coding: utf-8 -*-
{
    'name': "POS: Block Price Below Cost Odoo Online, Odoo.sh, On Premise",
    'version': '1.0.3',
    'summary': """
        Prevents selling products below their cost price in the Point of Sale.
    """,
    'description': """
        This module enhances the Point of Sale by adding two layers of protection:
        1. It logs a warning in the browser console/alert if a price is set below cost in real-time.
        2. It performs a final check before payment and blocks the transaction if any product is priced below cost, showing a detailed alert to the user and auto-correcting the prices.
    """,
    'author': "Nirav Rathod",
    'category': 'Sales/Point of Sale',
    'depends': ['point_of_sale'],
    'assets': {
        'point_of_sale._assets_pos': [
            'nr_restrict_under_cost_pos/static/src/js/pos_price_check.js',
        ],
    },
    'images': ['static/src/description/cover.gif'],
    'icon': 'static/src/description/icon.png',
    'installable': True,
    'application': False,
    'license': 'OPL-1',
}
