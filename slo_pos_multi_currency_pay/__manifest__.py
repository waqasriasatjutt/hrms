{
    'name': "Multi Currency Payment for PoS",
    'category': 'Point of Sale',
    'summary': "Enable Multi-Currency Payment in PoS",
    'author': 'Saw Lwin Oo(Duskwrath)',
    'depends': ['point_of_sale', 'account',],
    'data': [
        'views/res_config_settings_views.xml'
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'slo_pos_multi_currency_pay/static/src/**/*',
        ],
    },
    'license': 'LGPL-3',
}
