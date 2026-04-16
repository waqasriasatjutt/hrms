{
    "name": "POS Invoice Auto Check",
    "version": "18.0",
    "category": "Point of Sale",
    "summary": "The POS Auto Invoice Check module streamlines the Odoo Point of Sale workflow by automatically activating the invoice option whenever a POS order is validated. This automation is especially valuable for businesses that must generate invoices for every transaction, ensuring compliance and consistent record-keeping. By removing the need for cashiers to manually select the invoice option, the module reduces errors, speeds up checkout, and improves overall operational efficiency. The POS Auto Invoice Check module enhances Odoo Point of Sale by automating the invoice selection process during checkout. By enabling a simple option in General Settings to INKERP, administrators can activate automatic invoice generation for all POS orders. This eliminates the need for cashiers to manually check the invoice option, ensuring every transaction is properly documented and aligned with accounting requirements. Once configured, the POS interface automatically displays the Invoice option as pre-checked on the payment screen, as shown in the screenshots. This improves workflow efficiency, reduces human error, and speeds up the checkout process-especially in fast-paced retail environments. The module provides a seamless and reliable way to maintain consistent invoicing without adding extra steps for POS users. Odoo POS Auto Invoice, POS Invoice Automation, Odoo Point of Sale Invoice, POS Auto Invoice Check, Odoo POS Invoice Module, Automatic Invoice Odoo, POS Invoice Default Checked, Auto invoice generator for POS, Invoice creation in POS, One-click invoice in POS, POS auto invoicing solution, POS retail invoice automation, Auto invoice backend integration, Easy invoice creation Odoo POS.",
    "author": "INKERP",
    "website": "www.inkerp.com",
    "depends": [
        "point_of_sale",
        "eg_app_base"
    ],
    "data": [
        "views/pos_config_view.xml"
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "eg_pos_auto_invoice_check/static/src/js/PosOrder.js"
        ]
    },
    "qweb": [],
    "images": [
        "static/description/banner.gif"
    ],
    "license": "OPL-1",
    "installable": True,
    "application": True,
    "auto_install": False,
    "price": "0.0",
    "currency": "EUR",
    "description": "The POS Auto Invoice Check module enhances Odoo Point of Sale by automatically enabling the invoice option during order validation. This helps businesses that require invoices for every POS transaction, improving accuracy and reducing manual steps for cashiers."
}