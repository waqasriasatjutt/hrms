{
    "name": "POS Remove Orderlines",
    "version": "18.0",
    "category": "Point of Sale",
    "summary": "POS Orderline Remover is a powerful yet simple enhancement for Odoo Point of Sale designed to make cart management faster, cleaner, and more efficient. This module introduces intuitive tools that allow cashiers to delete individual product lines or clear the entire cart with a single click, eliminating time-consuming manual adjustments. Whether a customer changes their order, products are added by mistake, or a cashier needs to start over quickly, this module provides the flexibility and speed required for a smooth POS workflow. With a built-in configuration option available directly in Odoo Settings, administrators can enable or disable the functionality without any technical knowledge, ensuring complete control over how the POS behaves. The delete icon added beside each order line helps staff operate more accurately, while the \u201cRemove All Line\u201d button offers a quick solution to reset the cart instantly. The module also provides a clean and user-friendly confirmation notification, making the entire process transparent and easy to follow. Designed for retail stores, restaurants, supermarkets, caf\u00e9s, and any business using Odoo POS, this module improves productivity by reducing unnecessary steps during checkout. It brings a modern, efficient, and intuitive experience to your POS environment while keeping the workflow fully compatible with core Odoo features. By simplifying cart corrections and reducing cashier workload, POS Orderline Remover helps businesses deliver faster service and a better customer experience. POS orderline remover,Odoo remove cart lines, POS clear cart button, Odoo POS delete orderline, Remove all lines in POS, Odoo POS cart management, POS line delete feature, POS cart cleanup, Orderline delete extension, Odoo POS enhancement, Easy POS cart reset, Delete product line POS, POS quick cart clear, Smart POS cart remover.",
    "description": "POS Orderline Remover is a lightweight and user-friendly Odoo module that enhances your Point of Sale by allowing cashiers to quickly delete individual order lines or clear the entire POS cart with a single click.",
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
            "eg_pos_remove_orderline/static/src/js/**/*",
            "eg_pos_remove_orderline/static/src/xml/**/*"
        ]
    },
    "demo": [],
    "license": "OPL-1",
    "installable": True,
    "application": True,
    "auto_install": False,
    "price": "0.0",
    "currency": "EUR",
    "images": [
        "static/description/banner.gif"
    ]
}