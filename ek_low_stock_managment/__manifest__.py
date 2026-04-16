# -*- coding: utf-8 -*-
{
    'name': "POS Low Stock Management",
    'version': '18.0',
    'summary': """Product Low Stock Alert Display in Point of Sale and 
    Product Views""",
    "category": 'Warehouse,Point of Sale',
    'description': """Module adds functionality to display product stock 
    alerts in the point of sale interface, indicating low stock levels for 
    products and also in the product variant kanban and list view.""",
    'company': "eK Solutions",
    'author': "eK Solutions",
    'website': "https://ek-solutions.odoo.com",
    'live_test_url': '',
    'price': 0,
    'currency': 'USD',
    'depends': ['stock', 'point_of_sale'],
    'data': [
        'views/res_config_settings_views.xml',
        'views/product_product_views.xml',
    ],
    'assets': {
        'web.assets_backend': [

        ],
        'point_of_sale._assets_pos': [
            'ek_low_stock_managment/static/src/css/display_stock.css',
            'ek_low_stock_managment/static/src/js/PaymentScreen.js',
            'ek_low_stock_managment/static/src/js/data_service.js',
            # 'ek_low_stock_managment/static/src/js/product_card.js',
            'ek_low_stock_managment/static/src/xml/product_item_template.xml',
        ],
    },
    'images': ['static/description/banner.gif'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
