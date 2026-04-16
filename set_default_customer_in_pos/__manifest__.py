{
    'name': "Set Default Customer In POS",

    'summary': "Automatically set a default customer in the Point of Sale.",

    'description': """
                Set Default Customer In POS is a functional enhancement for Odoo Point of Sale that allows
                administrators to configure a default customer for POS sessions. When enabled, the selected
                customer is automatically assigned in the POS interface, reducing manual selection and
                improving billing efficiency during sales operations.
    """,
    'author': "Vishnu Sasikumar",
    'category': 'Point of Sale',
    'version': '18.0.1.0.0',
    'depends': ['base', 'point_of_sale'],

    'data': [
        'views/pos_config_views.xml'
    ],
     'assets': {
        'point_of_sale._assets_pos': [
            'set_default_customer_in_pos/static/src/js/pos_order.js',
        ],
    },

    'images': ['static/description/banner.png'],

    'license': "LGPL-3",
    'installable': True,
    'application': True,
    'auto_install': False,
}
