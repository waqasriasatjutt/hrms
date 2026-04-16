# -*- coding: utf-8 -*-
{
    'name': 'Sales Item Summary Report',
    'version': '1.1',
    "summary": "Generate Sales Item Summary in PDF or Excel",
    'depends': ['base', 'sale', 'sale_management', 'point_of_sale', 'report_xlsx'],

    'author': 'Waqas Riasat',
    'license': 'AGPL-3',
    'maintainer': 'Waqas Riasat',
    'company': 'Waqas Riasat',
    'website': 'https://way4tech.cloud',

    'license': 'LGPL-3',
    "category": 'Reporting',

    'data': [
        'security/ir.model.access.csv',

        'wizards/wizard_view.xml',

        'views/action_report.xml',
        'views/sale_item_summary_template.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
