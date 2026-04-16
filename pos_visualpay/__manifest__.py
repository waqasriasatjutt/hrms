{
    "name": "POS VisualPay",
    'version': '18.0.1.0',
    "summary": "Integración visual para métodos de pago en el POS",
    "description": """Este módulo agrega opciones visuales y de confirmación a los métodos de pago del POS.
- Imagen y descripción en el método de pago
- Confirmación de pago con captura
- Integración visual en la interfaz del POS""",
    "author": "Ernesto Pacheco",
    "category": "Point of Sale",
    "depends": ["base","point_of_sale"],
    "data": [
        "views/pos_payment_method_views.xml",
        "security/ir.model.access.csv",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_visualpay/static/src/**/*"
        ],
    },
    'website': "https://github.com/EpOpenLabs/Odoo-Open/tree/18.0/pos_visualpay",
    'images': ['static/description/banner.png'],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
