# pos_copy_cash/__manifest__.py
{
    "name": "POS Copy Cash Amount",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "category": "Point of Sale",
    "summary": "Add a Copy Cash button to the POS Close Session popup to Copy Cash Amount",
    "author": "Apurva Wanjari",
    "depends": ["point_of_sale"],
    "data": [],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_copy_cash/static/src/js/copy_cash_amount.js",
        ],
    },
    "images": ['static/description/banner.png'],
    "installable": True,
    "auto_install": False,
}
