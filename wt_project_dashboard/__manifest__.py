# -*- coding: utf-8 -*-
{
    'name': 'WT Project Analytics Dashboard',
    'version': '18.0.1.0.0',
    'category': 'Project',
    'sequence': 55,
    'summary': 'Enterprise Project Analytics Dashboard — KPIs, Tasks, Team Performance, Timeline & Comparison for Odoo 18',
    'description': """
WT Project Analytics Dashboard — Enterprise Edition for Odoo 18

A professional, fully responsive Project analytics dashboard with real-time KPIs,
task tracking, team workload, deadline monitoring and project-level filtering.

PRICING
-------
One-time purchase. No subscription, no recurring fees.
A single purchase covers Odoo 18.

Key Features:
- 10 KPI cards: Active Projects, Total Tasks, Done Tasks, Overdue Tasks, Due Today,
                Team Members, No Deadline, High Priority, Created in Period, Completion %
- 5 Tabs: Overview, Tasks, Team, Timeline, Comparison
- Smart Filters: Period, Custom Date Range, Project selector
- Charts: Task Status breakdown, Tasks by Assignee, Overdue vs On-time trend,
          Completion rate over time, Priority distribution, Team workload, Period Comparison
- Overdue task list with assignee and deadline
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
    'depends': ['project', 'web'],
    'data': [
        'views/dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js',
            'wt_project_dashboard/static/src/css/dashboard.css',
            'wt_project_dashboard/static/src/xml/dashboard.xml',
            'wt_project_dashboard/static/src/js/dashboard.js',
        ],
    },
    'application': True,
    'installable': True,
}
