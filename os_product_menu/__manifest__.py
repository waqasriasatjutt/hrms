# -*- coding: utf-8 -*-
{
    'name': 'PoS Product Menu',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Adds a top-level menu for Point of Sale Products',
    'description': """
        This module adds a new top-level menu item named "Produits"
        which links directly to the list of products available in the
        Point of Sale.
    """,
    'author': 'OUAHDA SOLUTIONS', # Replace with your name or company
    'website': 'https://www.ouahdasolutions.com', # Optional: Replace with your website
    'depends': [
        'point_of_sale', # Depends on the Point of Sale module
        'product',       # Depends on the base product module
        ],
    'data': [
        'views/menu.xml', # Load the menu definition file
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
