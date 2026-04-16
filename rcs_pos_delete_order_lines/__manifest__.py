# -*- coding: utf-8 -*-
{
    'name': "Remove Order Line In POS",
    'version': '18.0.0.0.0',
    'category': 'Point of Sale',
    'summary': """
            Quickly manage order lines in POS with a one-click remove option.  
            Add a cross icon for deleting items instantly and a "Clear All" button to reset orders.  
            Boost cashier efficiency, speed up checkout, and reduce errors in retail POS.
            PO system,PO management,order receipt,po software,po mangement software,point of sale system,remove product,order cancel,sales order tracking software,ordercounter pos,order management system,retail pos system,remove item,delete line,remove order,point of sale software,retail pos,best point of sale system,retail pos software,top pos systems for retail,order system,pos billing software,delete object online
    """,

    'description': """
            Quickly manage order lines in POS with a one-click remove option.  
            Add a cross icon for deleting items instantly and a "Clear All" button to reset orders.  
            Boost cashier efficiency, speed up checkout, and reduce errors in retail POS.
            PO system,PO management,order receipt,po software,po mangement software,point of sale system,remove product,order cancel,sales order tracking software,ordercounter pos,order management system,retail pos system,remove item,delete line,remove order,point of sale software,retail pos,best point of sale system,retail pos software,top pos systems for retail,order system,pos billing software,delete object online
    """,

    'author': 'Reliution',
    'website': "https://www.reliution.com",

    'maintainer': "Reliution",
    'depends': ['point_of_sale'],

    'images': ['static/description/banner.gif'],

    'assets': {
        'point_of_sale._assets_pos': [
            'rcs_pos_delete_order_lines/static/src/css/button.css',
            'rcs_pos_delete_order_lines/static/src/app/control_buttons/control_buttons.js',
            'rcs_pos_delete_order_lines/static/src/app/control_buttons/control_buttons.xml',
            'rcs_pos_delete_order_lines/static/src/app/screens/product_screen/product_screen.js',
            'rcs_pos_delete_order_lines/static/src/app/screens/product_screen/product_screen.xml',
        ],
    },

    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
    'data': [
        'security/ir.model.access.csv',
        'wizard/extends_support_wizard.xml',
    ],
    'live_test_url': "https://www.reliution.com/odoo-app-store?app_name=rcs_pos_delete_order_lines&app_version=18.0&odoo_type=Community"
}
