{
    'name': 'Products and Units Overview',
    'version': '1.1',
    'category': 'Point of Sale',
    'summary': "Display the total number of items and the total quantity ordered in the Point Of Sale.",
    'description': "This application displays the total number of products ordered"
                   "as well as the cumulative quantity of items in the order summary on the POS screen and printed bill.",
    'author': 'Techmatic Systems',
    'company': 'Techmatic Systems',
    'maintainer': 'Techmatic Systems',
    'website': 'https://www.techmaticsys.com',
    'depends': ['point_of_sale'],
    'data': [
        'views/app_config_settings_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'Products_Units_Overview/static/src/components/order_receipt_summary.js',
            'Products_Units_Overview/static/src/components/order_receipt_summary.xml',
            'Products_Units_Overview/static/src/components/order_widget_m.js',
            'Products_Units_Overview/static/src/components/order_widget_m.xml',
       ],
    },
    'images': ['static/description/icon.png',
            
              ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}