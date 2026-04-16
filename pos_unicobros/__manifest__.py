{
    'name': 'POS Unicobros',
    'category': 'Sales/Point of Sale',
    'author': 'Ivan Arriola - Quay',
    'sequence': 6,
    'summary': 'Integrate your POS with the Unicobros payment terminal',
    'data': [
        'views/pos_payment_method_views.xml',
    ],
    'website': 'https://www.unicobros.com.ar/',
    'version': "18.0.1.0.0",
    'images':  ['static/description/portada.png'],
    'depends': ['point_of_sale'],
    'installable': True,
    'application': True,
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_unicobros/static/**/*',
        ],
    },
    'license': 'LGPL-3',
}
