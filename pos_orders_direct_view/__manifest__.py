# -*- coding: utf-8 -*-
{
    'name': "POS Orders Direct View",

    'summary': "Direct button to view active orders from POS navbar",

    'description': """
        POS Orders Direct View
        ======================

        This module adds a direct "Orders" button to the Point of Sale navbar, 
        providing instant access to the ticket screen for viewing and managing 
        active orders without navigating through multiple menus.

        Key Features:
        * One-click access to orders screen
        * Improved cashier workflow efficiency
        * Touch-friendly button design
        * No configuration required
        * Seamless integration with existing POS interface
    """,

    'author': "PyBeans",
    'website': "https://www.pybeans.com",
    'maintainer': "PyBeans",
    'support': "devpybeans@gmail.com",
    'license': "LGPL-3",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Point of Sale',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['point_of_sale'],

    'data': [],

    'assets': {
        'point_of_sale._assets_pos': [
            'pos_orders_direct_view/static/src/xml/navbar.xml'
        ]
    },

    'images': ['static/description/order_view_button.png'],

    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 0,
    'currency': 'USD',
}

