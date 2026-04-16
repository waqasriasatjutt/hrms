{
    "name": "POS Thai QR30 - SCB",
    "version": "1.0",
    "category": "Sales/Point of Sale",
    'author': "Chanuwat NC",
    "license": "AGPL-3",
    'installable': True,
    'application': False,
    "auto_install": False,
    "depends": ["point_of_sale"],
    "summary": "Integrate your POS with QR code payment provided by SCB. Compatible with PromptPay.",
    "data": [
        "security/ir.model.access.csv",
        "views/pos_payment_method_views.xml",
        "views/pos_payment_views.xml"
    ],
    'images': [
        'static/description/setup1.png',
        'static/description/setup2.png',
        'static/description/usage1.png',
        'static/description/usage2.png',
        'static/description/receipt1.png',
        'static/description/history1.png',
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            'pos_qr30_scb/static/src/app/pos_app.js',
            'pos_qr30_scb/static/src/app/models/pos_order.js',
            'pos_qr30_scb/static/src/app/models/pos_payment.js',
            'pos_qr30_scb/static/src/app/utils/qr_code_popup/qr_code_popup.js',
            'pos_qr30_scb/static/src/app/screens/payment_screen/payment_screen.js',
            'pos_qr30_scb/static/src/app/screens/payment_screen/payment_line/payment_lines.xml',
            'pos_qr30_scb/static/src/app/utils/qr_code_popup/qr_code_popup.xml',
            'pos_qr30_scb/static/src/app/store/pos_store.js',
        ],
        'point_of_sale.customer_display_assets': [
            'pos_qr30_scb/static/src/customer_display/customer_display.js',
            'pos_qr30_scb/static/src/customer_display/customer_display.xml',
            'pos_qr30_scb/static/src/app/utils/customer_display_qr_popup/customer_display_qr_popup.js',
            'pos_qr30_scb/static/src/app/utils/customer_display_qr_popup/customer_display_qr_popup.xml',
        ],
    },
}
