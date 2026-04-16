{
    'name': 'POS Tax Invoice Receipt',
    'version': '18.0.1.0.0',
    'summary': 'Customize POS receipt with Tax Invoice heading and VAT No',
    'author': "Diode Info Solutions",
    'website': 'https://www.diodeinfosolutions.com/',
    'category': 'Point of Sale',
    'description': """
    This module customizes the Point of Sale receipt:
    - Adds "TAX INVOICE" heading
    - Shows company VAT number
    - Removes "Powered by Odoo"
    """,
    'depends': ['point_of_sale'],
    'data': [],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_receipts/static/src/xml/pos_receipt.xml',
            'pos_receipts/static/src/xml/pos_receipt_updates.xml',
            'pos_receipts/static/src/xml/pos_receipt_address.xml',
            'pos_receipts/static/src/js/pos_order_patch.js',

        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}




