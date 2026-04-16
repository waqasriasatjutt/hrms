{
    'name': "Product Stock Alert ( Low Stock )",
    'version': '18.0.1.0.0',
    'category': 'Inventory, Point of Sale',
    'author': 'Evnaz',
    'summary': 'Visual low stock alerts in Products and POS',
    'depends': ['product', 'point_of_sale'],
    'data': [
        'views/res_config_settings_views.xml',
        'views/product_product_views.xml',
        'views/product_template_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'product_stock_low_alert/static/src/css/stock_alert.css',
        ],
        'point_of_sale._assets_pos': [
            'product_stock_low_alert/static/src/xml/product_stock_badge.xml',
        ],
    },
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}
