{
    'name': 'WT Odoo Custom Color',
    'version': '0.1',
    'summary': 'Change header/Footer Color in backend/frontend',
    'author': 'Waqas Riasat',
    'license': 'AGPL-3',
    'maintainer': 'Waqas Riasat',
    'company': 'Waqas Riasat',
    'website': 'https://way4tech.cloud',
    'depends': [
        'web',
        'website',
        'point_of_sale',
    ],
    'category':'App',
    'description': """
           Way4tech Odoo Change header/Footer Color in backend/frontend
    """,
    'assets': {
        'web.assets_backend': [
            '/wt_custom_color/static/src/scss/wt_custom.css',
        ],

        'web.assets_frontend': [
             '/wt_custom_color/static/src/scss/web_custom.css',
        ],

        'point_of_sale._assets_pos': [
            '/wt_custom_color/static/src/scss/pos_custom.css',
        ],
    },
    'installable': True,
    'application': True,
}
