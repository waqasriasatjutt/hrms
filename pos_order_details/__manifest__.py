{
    "name": "pos_order_details",
    "summary": "POS Order Details",
    "category": "Sales/Point of Sale",
    "version": "18.0.1.0.0",
    "depends": [
        "point_of_sale",
    ],
    "author": "BizzAppDev Systems Pvt. Ltd.",
    "website": "http://www.bizzappdev.com",
    "license": "Other proprietary",
    "images": ["images/Pos_Details.gif"],
    "installable": True,
    "data": [
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "point_of_sale.assets_prod": [
            "pos_order_details/static/src/css/Popups/order_info_popup.css",
            "pos_order_details/static/src/js/Popups/order_details_popup.esm.js",
            "pos_order_details/static/src/js/TicketScreen/ticket_screen.esm.js",
            "pos_order_details/static/src/xml/Popups/OrderDetailsPopup.xml",
            "pos_order_details/static/src/xml/TicketScreen/TicketScreen.xml",
        ],
    },
}
