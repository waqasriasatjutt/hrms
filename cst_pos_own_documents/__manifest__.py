# -*- coding: utf-8 -*-

{
    "name": "POS Read Own Documents",
    "summary": "Restrict POS users to access only their own documents.",
    "description": """
        POS Read Own Documents allows businesses to restrict Point of Sale users
        to view only their own POS-related records.

        When enabled via a dedicated security group, users can access only:
        - Their assigned POS configurations
        - Their own POS sessions
        - Their own POS orders
        - Payments related to their own orders
        
    """,
    "author": "CodeSphere Tech",
    "website": "https://www.codespheretech.in/",
    "category": "Point Of Sale",
    "version": "18.0.1.0.0",
    "sequence": 0,
    "currency": "USD",
    "price": 0.0,
    "depends": ["base", "point_of_sale", ],
    "data": [
        'security/point_of_sale_user_security.xml',
        'views/res_config_settings_views.xml',
    ],
    "images": [
        "static/description/Banner.png",
    ],
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "auto_install": False,
}
