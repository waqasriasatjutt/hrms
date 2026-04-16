{
    "name": "POS Numpad",
    "summary": "POS Numpad",
    "category": "Sales/Point of Sale",
    "version": "18.0.1.0.1",
    "depends": [
        "point_of_sale",
    ],
    "author": "BizzAppDev Systems Pvt. Ltd.",
    "website": "http://www.bizzappdev.com",
    "license": "Other proprietary",
    "images": ["images/pos_numpad.png"],
    "installable": True,
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_numpad/static/src/src/js/numpad.esm.js",
            "pos_numpad/static/src/src/js/ticket_screen.esm.js",
        ],
    },
}
