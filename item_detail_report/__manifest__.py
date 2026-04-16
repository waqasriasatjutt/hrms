{
    'name': 'Item Detail Report',
    'version': '18.0.1.0',
    'summary': 'Product-wise Sales Detail Report',
    'category': 'Sales',
    'author': 'Way4Tech',
    'depends': ['sale_management', 'report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/item_detail_wizard_view.xml',
        'report/item_detail_report.xml'],
    'installable': True}
