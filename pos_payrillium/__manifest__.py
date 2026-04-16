# Used to define module metadata, dependencies and asset loading
{
    'name': 'Payrillium Payment',
    'version': '18.0.1.1.3',
    'depends': ['point_of_sale', 'payment', 'account', 'web'],
    'author': 'PAYRILLIUM',
    'category': 'Point of Sale',
    'license': 'OPL-1',
    'summary': 'Payrillium Payment Integration',
    'description': """
Integrates Odoo POS and Invoicing with Payrillium/Mirillium payment services to support:
- Physical payment terminals
- Tokenized payments
- Pay-by-link
- Refunds
- Session-scoped terminal selection

This module communicates with Payrillium/Mirillium external APIs. A valid account and API token are required for full functionality.
If the external service is unavailable, the module will display errors and will not process payments until connectivity is restored.
""",
    'post_init_hook': 'show_payrillium_wizard_once',
    'uninstall_hook': 'uninstall_cleanup_payrillium',
    'data': [
        'views/accounting_invoicing_action_sync_history.xml',
        'views/accounting_invoicing_payment_create_token_wizard.xml',
        'views/accounting_invoicing_payment_token_action.xml',
        'views/accounting_invoicing_payment_list_token.xml',
        'views/accounting_invoicing_list_actions_buttons.xml',
        'views/accounting_invoicing_buttons_payment.xml',
        'views/accounting_invoicing_payment_link_views.xml',
        'views/accounting_invoicing_configuration_set_paybylink_menu.xml',
        'views/accounting_invoicing_payment_link_wizard_patch.xml',
        'data/ir_cron_data.xml',

        'views/patch_payment_transaction_form.xml',
        'security/ir.model.access.csv',
        'views/pos_payment_method_views.xml',
        "data/data.xml",
        'views/res_config_settings.xml',
        'views/payrillium_terminal_views.xml',
        'views/patch_payment_transaction_list.xml',
        'views/pos_config_form_terminal.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'pos_payrillium/static/src/css/status_colors.scss',
            'pos_payrillium/static/src/js/payment_link_wizard.js',
            'pos_payrillium/static/src/js/sync_button.js',
            'pos_payrillium/static/src/xml/sync_button.xml',
            'pos_payrillium/static/src/js/loading_indicator_patch.js',
            'pos_payrillium/static/src/js/chatter_payment_link.js',
            'pos_payrillium/static/src/js/notification_handler.js',
            'pos_payrillium/static/src/css/loader.css',
            'pos_payrillium/static/src/css/token_wizard.css',
            'pos_payrillium/static/src/css/pay_by_token_form_fix.css',
            'pos_payrillium/static/src/css/payment_link_chatter.css'
        ],
        'point_of_sale._assets_pos': [
            'pos_payrillium/static/src/xml/chrome_patch.xml',
            'pos_payrillium/static/src/xml/pos_terminal_status.xml',
            'pos_payrillium/static/src/js/api_service.js',
            'pos_payrillium/static/src/js/config_loader.js',
            'pos_payrillium/static/src/js/order_models.js',
            'pos_payrillium/static/src/js/order_patch.js',
            'pos_payrillium/static/src/js/order_receipt_patch.js',
            'pos_payrillium/static/src/js/payment_handler.js',
            'pos_payrillium/static/src/js/payment_screen.js',
            'pos_payrillium/static/src/js/patch_pos_store.js',
            'pos_payrillium/static/src/js/product_screen.js',
            'pos_payrillium/static/src/js/order_summary.js',
            'pos_payrillium/static/src/js/setup_config.js',
            'pos_payrillium/static/src/js/terminal_service.js',
            'pos_payrillium/static/src/js/ticket_screen.js',
            'pos_payrillium/static/src/js/utils.js',
            'pos_payrillium/static/src/css/payrillium.css',

            'pos_payrillium/static/src/js/navbar_patch.js',
            'pos_payrillium/static/src/xml/order_receipt_template.xml',

        ],
    },
    'icon': '/pos_payrillium/static/description/icon.png',
    'images': ['static/description/icon.png'],
    'installable': True,

    'application': True,
    'auto_install': False,
}
