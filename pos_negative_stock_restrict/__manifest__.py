{
    'name': "Pos Negative Stock Restriction",

    'summary': "Prevents selling products with insufficient stock in Odoo POS to avoid negative inventory.",

    'description': """ This module restricts the validation of POS orders when product stock is insufficient, ensuring that negative stock is not allowed in the Point of Sale.""",

    'author': "Vishnu Sasikumar",
    'category': 'Point of Sale',
    'version': '18.0.2.0.0',
    'depends': ['base','point_of_sale','stock'],

    'data': [],
    'assets': {'point_of_sale._assets_pos': [
        'pos_negative_stock_restrict/static/src/js/product_screen.js',
    ]},
    'images': ['static/description/banner.png'],
    'license':"LGPL-3",
    'installable': True,
    'application': True,
    'auto_install': False,
}

