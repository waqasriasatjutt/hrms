{
    'name': 'Simple Online Users',
    'version': '17.1',
    'category': 'Website/Tools',
    'author': 'Paulius Gaizauskas',
    'maintainer': 'Paulius Gaizauskas',
    'website': 'https://github.com/Paulius11/simple-online-users',
    'email': 'paulius.gaizauskas@gmail.com',
    'summary': 'Display online users count in systray - Free version',
    'description': """
Simple Online Users - Free Edition
==================================

A lightweight module that displays the count of currently online users in the Odoo systray.

Key Features:
* Real-time online user count display
* Clean systray integration  
* Uses Odoo's built-in bus.presence system
* No custom models or complex setup required
* Configurable visibility permissions
* Popup showing detailed user list with status

Perfect for teams who want to see who's currently active in their Odoo system.

🔹 This is the FREE version with essential features
🔹 Advanced version available with additional configuration options and features

Technical Details:
* Leverages native bus.presence infrastructure
* Automatic status detection (online/away/offline)
* Lightweight with minimal resource usage

Installation:
Simply install the module and the online users count will appear in your systray.
Configure visibility permissions in Settings > General Settings > Online Users.
    """,
    'depends': ['base', 'web', 'bus'],
    'data': [
        'data/config_data.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'simple_online_users/static/src/js/online_users.js',
            'simple_online_users/static/src/xml/online_users.xml',
        ],
    },
    'images': ['static/description/banner.png', 'static/description/icon.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
    'price': 0.00,
    'currency': 'EUR',
    'support': 'paulius.gaizauskas@gmail.com',
    'live_test_url': '',
}