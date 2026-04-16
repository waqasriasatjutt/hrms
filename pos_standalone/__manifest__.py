{
    'name': 'POS Standalone',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Standalone Point of Sale - Offline First PWA',
    'description': """
POS Standalone - Offline First Point of Sale
=============================================

A fully functional Point of Sale application that works offline-first.

Features:
---------
* 📱 Progressive Web App (PWA) - Install on any device
* 💾 Offline Mode - All data stored locally in IndexedDB
* 🌐 Online Mode - Sync with Odoo server
* 🔄 Database Export/Import - Backup and restore functionality
* 🔐 PIN Security - Session-based locking
* 📊 Multi-tab Order Management
* 💰 Multiple Payment Methods
* 👥 Customer Management
* 📦 Product & Category Management
* 🏷️ Pricelist Support
* 🧾 Receipt Printing

Technical:
----------
* Built with Owl.js framework
* IndexedDB via Dexie.js
* Works on file:// protocol
* No external dependencies required
* Single HTML file distribution

Usage:
------
1. Install the module in Odoo
2. Access via menu: Point of Sale > POS Standalone
3. Or download the standalone HTML file for offline use

Author: Your Company
License: LGPL-3
    """,
    'author': 'Your Company',
    'website': 'https://linkedin.com/in/okky-permana-sihipo',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'point_of_sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_standalone_views.xml',
        'views/pos_standalone_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'pos_standalone/static/src/**/*',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
