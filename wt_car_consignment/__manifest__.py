# -*- coding: utf-8 -*-
{
    "name": "Car Consignment Management",
    "version": "1.0",
    "category": "Sales",
    "summary": "Manage consignment car sales with profit-only accounting",
    "description": """
Car Consignment Management allows you to handle vehicle sales where cars are sold
on behalf of owners while only the commission or profit is recognized as company income.

Key Features:
• Register cars as consignment products
• Assign car owner and expected sale price
• Track purchase, expenses, and selling price
• Generate customer invoices via wizard
• Automatically post only profit to income accounts
• Track vehicle-related expenses
• Full integration with Sales, Accounting, Stock, and Website Shop

This module is ideal for car dealerships and showrooms working on consignment
or third-party vehicle sales.

Compatible with Odoo 18 & Odoo 19.
    """,

    "author": "Waqas Riasat",
    "company": "WAY4TECH",
    "maintainer": "Waqas Riasat",
    "website": "https://www.way4tech.com",
    "support": "info@way4tech.com",

    "license": "LGPL-3",

    "depends": [
        "base",
        "sale",
        "account",
        "stock",
        "website_sale",
    ],

    "data": [
        "security/ir.model.access.csv",
        "wizard/car_sale_invoice_wizard.xml",
        "views/product_template_views.xml",
        "views/car_expense_views.xml",
        "views/abc.xml",
    ],

    "assets": {
        # Add if needed later
        # "web.assets_backend": [],
    },

    "images": [
        "static/description/banner.png",
    ],
      "price": 199,
    "currency": "USD",
    "installable": True,
    "application": False,
    "auto_install": False,
}
