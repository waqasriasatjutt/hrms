{
    "name": "POS eID Scan (Belgium)",
    "version": "18.0.1.0.2",
    "category": "Point of Sale",
    "summary": "Scan Belgian eID cards to create customers in POS",
    "author": "Said Imran",
    "website": "https://gitlab.com/imran.afr/odoo-module-eid-reader",
    "description": """
        This module adds a "Scan ID" button to the POS customer list.
        When clicked, it reads data from a Belgian eID card via a local bridge
        application and automatically creates a new customer with the scanned data.
        
        Requirements:
        - eID Bridge application running on http://127.0.0.1:8765
        - Belgian eID card reader connected to the computer
        
        Download the eID Bridge from: https://gitlab.com/imran.afr/odoo-module-eid-reader
    """,
    "depends": ["point_of_sale"],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_eid_reader/static/src/xml/pos_eid_scan.xml",
            "pos_eid_reader/static/src/js/pos_eid_scan.js",
        ],
    },
    "icon": "static/description/icon.png",
    "images": [
        "static/description/Screenshot_1.png",
        "static/description/Screenshot_2.png",
        "static/description/Screenshot_3.png",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}