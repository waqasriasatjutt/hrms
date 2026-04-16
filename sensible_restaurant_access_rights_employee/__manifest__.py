# Powered by Sensible Consulting Services
# -*- coding: utf-8 -*-
# © 2025 Sensible Consulting Services (<https://sensiblecs.com/>)
{
    'name': 'Smart POS Restaurant Access Rights | Smart Access Control for Restaurant POS | Restaurant Cashier Permissions | Smart Floor Access Control',
    'version': '18.0.1.0',
    'summary': 'Smart Access Control for Restaurant POS - Manage employee permissions and floor access with smart restaurant POS access rights',
    'description': '''
        Smart Access Control for Restaurant POS:
        ========================================
        Smart POS Restaurant Access Rights Management for complete control over
        restaurant-specific POS features for each employee.

        Smart Restaurant Actions Controls:
        - Smart Hide/Show Split Button
        - Smart Hide/Show Guests Button
        - Smart Hide/Show Transfer/Merge Button
        - Smart Hide/Show Transfer Course Button
        - Smart Hide/Show Bill Button
        - Smart Hide/Show Edit Order Name Button

        Smart Navigation Controls:
        - Smart Hide/Show Order Button
        - Smart Hide/Show Switch Floor View

        Smart Floor Access Control:
        - Smart disable specific floors per employee
        - Restrict employee access to specific restaurant floors
    ''',
    'category': 'Sales/Point of Sale',
    'author': 'Sensible Consulting Services',
    'website': 'https://sensiblecs.com',
    'license': 'AGPL-3',
    'depends': ['sensible_pos_access_rights_employee', 'pos_restaurant'],
    'auto_install': True,
    'data': [
        'views/sbl_hr_employee_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'sensible_restaurant_access_rights_employee/static/src/**/*',
        ],
    },
    'images': ['static/description/banner.png'],
    'application': True,
    'installable': True,
}
