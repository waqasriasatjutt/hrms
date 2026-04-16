# -*- coding: utf-8 -*-
{
    'version': '1.0.6',
    'name': 'Compago – Pagos con Terminales en Autoservicio/Kiosko',
    'summary': 'Integra terminales de Compago en la aplicación de autoservicio/kiosko para que los clientes puedan pagar con tarjeta de forma autónoma.',
    'description': """
        Este módulo extiende la funcionalidad de autoservicio/kiosko del Punto de Venta (POS) de Odoo, integrando terminales de Compago como método de pago.

        Permite que los clientes realicen pedidos y paguen directamente con tarjeta desde dispositivos de autoservicio, conectando con terminales físicas de Compago sin intervención del personal.

        Ideal para restaurantes, cafeterías y comercios que buscan ofrecer una experiencia de autoservicio completa y segura. Compago ofrece una solución moderna y eficiente para pagos desatendidos.
    """,

    'author': 'Compago',
    'website': 'https://www.compago.com',

    'category': 'Sales/Point of Sale',
    'license': 'OPL-1',

    'depends': ['pos_compago', 'pos_self_order'],

    'assets': {
        'pos_self_order.assets': [
            'pos_self_order_compago/static/**/*',
        ],
    },

    'installable': True,
    'auto_install': False,
    'application': False,
}
