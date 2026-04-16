{
    'name': "Recent Purchase Price",
    'version': '18.0.1.0.0',
    'summary': 'Last Purchase price of the Product',
    'author': "Diode Info Solutions",
    'website': 'https://www.diodeinfosolutions.com/',
    'category': 'Point of Sale',
    'description': """ This module allows to track the last purchase price of the product""",
    'depends': ['purchase'],
    'data': [
        'views/purchase_order_line.xml',
    ],

    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
