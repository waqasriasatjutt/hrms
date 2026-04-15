# -*- coding: utf-8 -*-
{
    'name': 'WT Inventory Analytics Dashboard',
    'version': '18.0.1.0.0',
    'category': 'Inventory',
    'sequence': 25,
    'summary': 'Enterprise Inventory Analytics Dashboard — KPIs, Stock Levels, Valuation, Movements & Alerts for Odoo 18',
    'description': """
WT Inventory Analytics Dashboard — Enterprise Edition for Odoo 18

A professional, fully responsive Inventory analytics dashboard with real-time KPIs,
stock level monitoring, low-stock alerts, valuation and movement tracking.

PRICING
-------
One-time purchase. No subscription, no recurring fees.
A single purchase covers Odoo 18.

Key Features:
- 9 KPI cards: Products in Stock, Stock Value, Low Stock Alerts, Out of Stock,
               Pending Receipts, Pending Deliveries, Stock Moves, Avg Product Value, Locations with Stock
- 5 Tabs: Overview, Stock Levels, Movements, Valuation, Comparison
- Smart Filters: Period, Custom Date Range, Warehouse/Location
- Charts: Stock Value by Category, Stock Movement Trend, Top Products by Quantity,
          Low Stock Items list, Receipts vs Deliveries, Valuation by Location, Period Comparison
- Real-time low-stock alert list with reorder recommendations
- Auto-refresh every 5 minutes
- Fully responsive — works on desktop, tablet and mobile
    """,
    'author': 'Waqas Riasat',
    'maintainer': 'Way4Tech',
    'website': 'https://way4tech.com',
    'support': 'support@way4tech.com',
    'license': 'OPL-1',
    'price': 20.0,
    'currency': 'USD',
    'images': ['static/description/banner.png'],
    'depends': ['stock', 'web'],
    'data': [
        'views/dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js',
            'wt_inventory_dashboard/static/src/css/dashboard.css',
            'wt_inventory_dashboard/static/src/xml/dashboard.xml',
            'wt_inventory_dashboard/static/src/js/dashboard.js',
        ],
    },
    'application': True,
    'installable': True,
}
