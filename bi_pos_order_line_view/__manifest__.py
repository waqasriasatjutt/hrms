# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    'name': 'POS Order Line View',
    'version': '18.0.0.0',
    'category': 'Point Of Sale',
    'summary': 'POS sales order line view point of sale order line view pos order line list view pos order line view point of sales order line view pos order line list view point of sales order line list view pos line view point of sale line view pos order line tree view',
    'description' :"""
        
        POS Order Line View Odoo App helps users to view POS order line in list view. User can shown POS order line in kanban view and form view also they can search by receipt number, product, salesperson, customer and session option then group by session, user, customer, status, order date, etc.

    """,
    'author': 'BROWSEINFO',
    'website': 'https://www.browseinfo.com/demo-request?app=bi_pos_order_line_view&version=18&edition=Community',
    'depends': ['base','point_of_sale'],
    'data': [
        'views/pos_view.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    "live_test_url":'https://www.browseinfo.com/demo-request?app=bi_pos_order_line_view&version=18&edition=Community',
    "images":['static/description/Banner.gif'],
}
