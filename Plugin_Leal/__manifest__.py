# -*- coding: utf-8 -*-
{
    'name': "Leal",
    'summary': "Modulo de integración con LEAL en Odoo POS",
    'description': """
        Este módulo permite a los usuarios redimir puntos LEAL acumulados en sus cuentas.
        Incluye funcionalidades para gestionar el proceso de redención, verificar puntos disponibles y realizar transacciones de redención.
    """,
    'author': "Leal Colombia SAS",
    'website': "https://www.leal.co",
    'category': 'Sales/Point of Sale',
    'version': '18.0.1.0.0',
    'price': 0.00,
    'currency': 'USD',
    'depends': ['base', 'point_of_sale'],
    'icon': 'static/description/icon.png',
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/res_config_settings_views.xml',
        'views/leal_user_data_views.xml',
        'views/leal_redeem_response_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'Plugin_Leal/static/src/css/leal_redeem.css',
        ],
        'point_of_sale._assets_pos': [
            # CSS
            'Plugin_Leal/static/src/css/leal_redeem.css',
            # JS
            # 'Plugin_Leal/static/src/js/api_utils.js',
            'Plugin_Leal/static/src/js/custom_control_button.js',
            # 'Plugin_Leal/static/src/js/document_input_popup.js',
            'Plugin_Leal/static/src/js/customer_search_popup.js',
            'Plugin_Leal/static/src/js/otp_input_popup.js',
            'Plugin_Leal/static/src/js/product_selection_popup.js',
            'Plugin_Leal/static/src/js/payment_extension.js',
            'Plugin_Leal/static/src/js/orderline_extension.js',
            'Plugin_Leal/static/src/js/payment_utils.js',
            'Plugin_Leal/static/src/js/pos_order_extension.js',
            'Plugin_Leal/static/src/js/leal_points_choice_popup.js',
            'Plugin_Leal/static/src/js/campaign_customer_extension.js',
            'Plugin_Leal/static/src/js/campaign_details_popup.js',
            'Plugin_Leal/static/src/js/campaign_redeem_utils.js',
            'Plugin_Leal/static/src/js/promotion_code_popup.js',
            # 'Plugin_Leal/static/src/js/paymentline_extension.js',
            # XML
            'Plugin_Leal/static/src/xml/custom_control_button.xml',
            # 'Plugin_Leal/static/src/xml/document_input_popup.xml',
            'Plugin_Leal/static/src/xml/customer_search_popup.xml',
            'Plugin_Leal/static/src/xml/otp_input_popup.xml',
            'Plugin_Leal/static/src/xml/product_selection_popup.xml',
            'Plugin_Leal/static/src/xml/leal_points_choice_popup.xml',
            'Plugin_Leal/static/src/xml/campaign_details_popup.xml',
            'Plugin_Leal/static/src/xml/promotion_code_popup.xml',
        ],
    },
    
    'images': [
        'static/description/images/PantallaInicial.png',
        'static/description/images/BuscaClientes.png',
        'static/description/images/SelecccionaProducto.png',
        'static/description/images/RedimeCodigoOTP.png',
        'static/description/images/ConfiguracionesMetododePago.png',
        'static/description/images/ProductoAgregadoGratis.png',
    ],
    
    'installable': True,
    'auto_install': False,
    'application': True,
    'license':'OPL-1',
}
