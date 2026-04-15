# -*- coding: utf-8 -*-
{
    'name': 'WT Accounting Analytics Dashboard',
    'version': '18.0.1.0.0',
    'category': 'Accounting',
    'sequence': 15,
    'summary': 'Enterprise Accounting Analytics Dashboard — KPIs, P&L, AR/AP Aging, Invoices & Comparison for Odoo 18',
    'description': """
WT Accounting Analytics Dashboard — Enterprise Edition for Odoo 18

A professional, fully responsive Accounting analytics dashboard with real-time KPIs,
P&L overview, accounts receivable/payable aging, invoice tracking and period comparison.

PRICING
-------
One-time purchase. No subscription, no recurring fees.
A single purchase covers Odoo 18.

Key Features:
- 9 KPI cards: Total Revenue, Total Expenses, Net Profit, Accounts Receivable,
               Accounts Payable, Outstanding Invoices, Overdue Invoices, Avg Invoice Value, Tax Collected
- 5 Tabs: Overview, P&L, AR/AP, Invoices, Comparison
- Smart Filters: Period, Custom Date Range
- Charts: Revenue vs Expenses trend, P&L waterfall, AR Aging buckets, AP Aging buckets,
          Invoice status breakdown, Monthly cash flow, Top customers by AR, Period Comparison
- Recent invoices list with status indicators
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
    'depends': ['account', 'web'],
    'data': [
        'views/dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js',
            'wt_accounting_dashboard/static/src/css/dashboard.css',
            'wt_accounting_dashboard/static/src/xml/dashboard.xml',
            'wt_accounting_dashboard/static/src/js/dashboard.js',
        ],
    },
    'application': True,
    'installable': True,
}
