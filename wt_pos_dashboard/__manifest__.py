# -*- coding: utf-8 -*-
{
    'name': 'WT POS Analytics Dashboard',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'sequence': 120,
    'summary': 'Enterprise POS Analytics Dashboard — KPIs, Charts, Filters, Comparison & Export for Odoo 18',
    'description': """
WT POS Analytics Dashboard — Enterprise Edition for Odoo 18

A professional, fully responsive POS analytics dashboard with real-time KPIs,
9 metric cards, 7 charts, 6 analytical tabs and smart filters including cashier,
terminal and custom date range. Includes CSV export.

PRICING
-------
One-time purchase. No subscription, no recurring fees.
A single purchase covers Odoo 18.

Key Features:
- 9 KPI cards: Revenue, Orders, Avg Order, Items Sold, Refunds, Sessions, Gross Margin, Discounts, Tax
- 6 Tabs: Overview, Financial, Products, Customers, Sessions, Comparison
- Smart Filters: Period, Custom Dates, Terminal, Cashier
- Export: Download all order lines as CSV
- Charts: Sales trend, Payment breakdown, Revenue vs Refunds, Hourly heatmap,
          Top Products (qty & revenue), Top Categories, Top Customers,
          New vs Returning customers, Discounts by Cashier, Gross Margin by Category,
          Average Revenue by Hour, Period Comparison
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
    'depends': ['point_of_sale', 'web'],
    'data': [
        'views/pos_order_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js',
            'wt_pos_dashboard/static/src/css/pos_dashboard.css',
            'wt_pos_dashboard/static/src/xml/pos_dashboard.xml',
            'wt_pos_dashboard/static/src/js/pos_dashboard.js',
        ],
    },
    'application': True,
    'installable': True,
}
