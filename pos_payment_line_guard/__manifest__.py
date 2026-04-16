{
    'name': 'POS - Guard Duplicate Zero Payment Line',
    'category': 'Point of Sale',
    'summary': """ Avoid duplicate payment lines with zero amount in POS 
                keywords: prevent duplicate payment line | avoid zero amount payment | prevent duplicate line | prevent zero line | POS prevent duplicate payment | POS avoid empty payment | prevent accidental payment line""",
    'description': """
            This module prevents the POS users from accidentally adding multiple unpaid payment lines 
            with zero amount for the same payment method.

            Key Features:
            - Prevents adding new payment lines when the due is zero.
            - Blocks adding a new zero-amount payment line if one already exists.
            - Optional configuration toggle in POS settings.
                    """,
    'author': 'Dustin Mimbela',
    'version': '1.0',
    'depends': ['point_of_sale'],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_payment_line_guard/static/src/**/*'
        ],
    },
    'data': ['views/pos.xml'],
    'installable': True,
    'auto_install': False,
    "license": "LGPL-3",
    "images": ["static/description/banner.png"],
}
