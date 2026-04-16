# Powered by Sensible Consulting Services
# -*- coding: utf-8 -*-
# © 2025 Sensible Consulting Services (<https://sensiblecs.com/>)
{
    'name': 'POS Timesheet',
    'version': '18.0.1.0',
    'category': 'Point of Sale',
    'summary': 'Timesheet integration with POS sessions',
    'description': """
        This module integrates timesheet functionality with POS sessions.
        Features:
        - Enable/disable timesheet creation from POS settings
        - Automatic timesheet check-in when POS session starts
        - Automatic timesheet check-out when POS session closes
        - View timesheet records from POS session via smart button
        - Real-time timer display in POS interface when timesheet is active
    """,
    'author': 'Sensible Consulting Services',
    'website': 'https://sensiblecs.com',
    'license': 'AGPL-3',
    'depends': ['hr_attendance', 'pos_hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/sbl_pos_config_views.xml',
        'views/sbl_pos_session_views.xml',
        'views/sbl_hr_attendance_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'sensible_pos_timesheet/static/src/js/sbl_pos_timer_widget.js',
            'sensible_pos_timesheet/static/src/js/sbl_pos_navbar.js',
            'sensible_pos_timesheet/static/src/js/sbl_opening_control_patch.js',
            'sensible_pos_timesheet/static/src/js/sbl_closing_popup_patch.js',
            'sensible_pos_timesheet/static/src/xml/sbl_pos_timer_widget.xml',
            'sensible_pos_timesheet/static/src/xml/sbl_pos_navbar.xml',
            'sensible_pos_timesheet/static/src/css/sbl_pos_timer_widget.css',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}