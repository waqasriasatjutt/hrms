{
    "name": "POS session invoice",
    "version": "18.0.0.0.0",
    "category": "Point of Sale",
    "summary": "Adds a default client field to POS configuration.",
    "description": """
        This module adds a new configuration field 'Customer by default'
        under the Point of Sale settings, specifically near 'Compte temporaire par défaut'.
    """,
    "author": "Info'Lib",
    "depends": ["point_of_sale"],
    "data": [
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
    "images": ["static/description/cover_540_270_pos_session_invoice.gif"],
}
