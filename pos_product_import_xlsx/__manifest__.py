{
    'name': 'POS Product Import from XLSX',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Import POS products from Excel (XLSX) file',
    'description': """
        Import products into Odoo POS from an Excel file.

        Supported columns:
        - Barcode
        - Cost
        - Sale Price
        - Point of Sale Category
        - Product Category
        - Supplier
        - Sale Taxes
        - Purchase Taxes
        - Available in POS
    """,
    'author': 'BarryJays',
    'depends': ['point_of_sale', 'product', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_import_wizard_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
