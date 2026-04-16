# -*- coding: utf-8 -*-
{
    'version': '1.0.6',
    'name': 'Compago – Pagos con Terminales Físicas en Punto de Venta',
    'summary': 'Integra terminales físicas de Compago al Punto de Venta de Odoo para aceptar pagos con tarjeta de forma segura y eficiente.',
    'description': """
        Este módulo integra Compago como proveedor de pagos con terminal físico en el sistema de Punto de Venta (POS) de Odoo.

        Permite procesar pagos con tarjeta directamente desde la interfaz del POS, conectando con terminales físicas sin necesidad de ingresar montos manualmente ni utilizar sistemas externos.

        Ideal para negocios que buscan una experiencia de cobro eficiente, fluida y segura. Compago ofrece una solución moderna y confiable para la gestión de pagos presenciales.
    """,

    'author': 'Compago',
    'website': 'https://www.compago.com',

    'category': 'Sales/Point of Sale',
    'license': 'OPL-1',

    'depends': ['point_of_sale'],

    'assets': {
        'point_of_sale._assets_pos': [
            'pos_compago/static/**/*',
        ],
    },

    'data': [
        'views/pos_payment_method_views.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': False,
}
