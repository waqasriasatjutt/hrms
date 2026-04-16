{
    'name': 'Daily Sales Report',
    'version': '18.0.1.0',
    'summary': 'Daily Sales Report with PDF & Excel',
    'category': 'Sales',
    'author': 'Way4Tech',
    'depends': ['sale_management','point_of_sale','report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/daily_sales_wizard_view.xml',
        'report/daily_sales_report.xml',
    ],
    'installable': True,
}
