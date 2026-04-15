# -*- coding: utf-8 -*-
{
    'name': 'WT CRM Analytics Dashboard',
    'version': '18.0.1.0.0',
    'category': 'CRM',
    'sequence': 56,
    'summary': 'Enterprise CRM Analytics Dashboard — KPIs, Pipeline, Leads, Team Performance & Comparison for Odoo 18',
    'description': """
WT CRM Analytics Dashboard — Enterprise Edition for Odoo 18

A professional, fully responsive CRM analytics dashboard with real-time KPIs,
pipeline tracking, lead analytics, team performance and period comparison.

PRICING
-------
One-time purchase. No subscription, no recurring fees.
A single purchase covers Odoo 18.

Key Features:
- 12 KPI cards: New Leads, Opportunities, Won Count, Won Revenue, Lost, Pipeline Count,
                Pipeline Value, Expected Revenue, Win Rate, Avg Deal Value, Team Members, Overdue Activities
- 5 Tabs: Overview, Pipeline, Leads, Team, Comparison
- Smart Filters: Period, Custom Date Range, Salesperson
- Charts: Pipeline by Stage, Won vs Lost trend, Lead Sources, Top Salespeople,
          Revenue by Month, Activity breakdown, Period Comparison
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
    'depends': ['crm', 'web'],
    'data': [
        'views/dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js',
            'wt_crm_dashboard/static/src/css/dashboard.css',
            'wt_crm_dashboard/static/src/xml/dashboard.xml',
            'wt_crm_dashboard/static/src/js/dashboard.js',
        ],
    },
    'application': True,
    'installable': True,
}
