# -*- coding: utf-8 -*-
{
    'name': 'WT Sales Analytics Dashboard',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'sequence': 35,
    'summary': 'Enterprise Sales Analytics Dashboard — KPIs, Products, Customers, Salespersons & Comparison for Odoo 18',
    'description': """
WT Sales Analytics Dashboard — Enterprise Edition for Odoo 18

A professional, fully responsive Sales analytics dashboard with real-time KPIs,
order tracking, product performance, customer insights and salesperson leaderboards.

PRICING
-------
One-time purchase. No subscription, no recurring fees.
A single purchase covers Odoo 18.

Key Features:
- 9 KPI cards: Total Revenue, Confirmed Orders, Avg Order Value, Quotations,
               Customers, Items Sold, Conversion Rate, Tax Collected, Pending Deliveries
- 6 Tabs: Overview, Financial, Products, Customers, Salespersons, Comparison
- Smart Filters: Period, Custom Date Range, Salesperson
- Charts: Revenue Trend, Order Status breakdown, Top Products, Top Customers,
          Salesperson Leaderboard, Monthly Revenue vs Target, Period Comparison
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
    'depends': ['sale', 'web'],
    'data': [
        'views/dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js',
            'wt_sale_dashboard/static/src/css/dashboard.css',
            'wt_sale_dashboard/static/src/xml/dashboard.xml',
            'wt_sale_dashboard/static/src/js/dashboard.js',
        ],
    },
    'application': True,
    'installable': True,
}
