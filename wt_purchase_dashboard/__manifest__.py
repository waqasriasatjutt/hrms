# -*- coding: utf-8 -*-
{
    'name': 'WT Purchase Analytics Dashboard',
    'version': '18.0.1.0.0',
    'category': 'Purchase',
    'sequence': 45,
    'summary': 'Enterprise Purchase Analytics Dashboard — KPIs, Vendors, Products, Payables & Comparison for Odoo 18',
    'description': """
WT Purchase Analytics Dashboard — Enterprise Edition for Odoo 18

A professional, fully responsive Purchase analytics dashboard with real-time KPIs,
vendor performance, spend analysis, bill tracking and period comparison.

PRICING
-------
One-time purchase. No subscription, no recurring fees.
A single purchase covers Odoo 18.

Key Features:
- 9 KPI cards: Total Spend, Purchase Orders, Avg PO Value, RFQs,
               Vendors, Items Ordered, Bills to Process, Overdue Bills, Tax Amount
- 5 Tabs: Overview, Financial, Vendors, Products, Comparison
- Smart Filters: Period, Custom Date Range, Vendor
- Charts: Spend Trend, Top Vendors by spend, Top Products by quantity,
          PO Status breakdown, Bills Aging, Monthly spend vs budget, Period Comparison
- Recent PO list with status indicators
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
    'depends': ['purchase', 'web'],
    'data': [
        'views/dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js',
            'wt_purchase_dashboard/static/src/css/dashboard.css',
            'wt_purchase_dashboard/static/src/xml/dashboard.xml',
            'wt_purchase_dashboard/static/src/js/dashboard.js',
        ],
    },
    'application': True,
    'installable': True,
}
