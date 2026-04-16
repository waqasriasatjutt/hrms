# -*- coding: utf-8 -*-

{
    'name': "PoS Hide Product Info",
    'category': 'Point of Sale',
    'summary': """Hide the Product Info ('i') Button in Odoo POS 
Easily control the visibility of the product info button for all users via POS configuration. Clean interface, better privacy.
'keywords': "hide product info | remove product details | block product information | hide info button | don't show product popup | stop showing item details | remove i button | hide extra info | prevent seeing product details | disable item description"
""",
    'description': """This module allows you to hide the Product Info ('i') button in the Odoo Point of Sale (POS) product screen for all users, based on POS configuration.\n\nKey Features:\n- Add a setting in POS configuration to hide/show the Product Info button.\n- No code or UI clutter: the button is cleanly removed when not needed.\n- Simple, robust and compatible with Odoo 17.\n- No impact on other POS features.\n\nIdeal for businesses that want to simplify the POS interface or restrict access to detailed product information for cashiers and staff.\n\nHow it works:\n- Go to POS > Configuration > Point of Sale.\n- Enable or disable 'Hide Product Info Button'.\n- The 'i' button will be hidden or shown accordingly in the POS product screen.\n""",
    'author': 'Dustin Mimbela',
    'version': '1.0',
    'depends': ['point_of_sale'],
    'data': [
       'views/res_config_setting_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_hide_product_info/static/src/js/product_card_patch.js',
        ]
    },
    'installable': True,
    'auto_install': False,
    "license": "LGPL-3",
    "images":["static/description/banner.gif"],
}

