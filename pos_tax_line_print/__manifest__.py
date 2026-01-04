{
    'name': 'POS Tax Line Print',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'Print tax indicators and summary in POS receipts',
    'author': 'Your Name',
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_receipt_template.xml',
        'views/assets.xml',
    ],
    'installable': True,
    'auto_install': False,
}