# -*- coding: utf-8 -*-
{
    'name': "hide_pos_cashcontrol_toggle",

    'summary': "Option to hide the Opening Cash Control popup in POS",

    'description': """
                This module adds a configuration option in POS settings to hide the Opening Cash Control popup 
                when a POS session is started.
                Ideal for businesses that do not want to enforce cash control for each session opening.""",

    'author': "Apurva Wanjari",
    'category': 'Point of Sale',
    'license': 'LGPL-3',
    'version': '18.0',
    'depends': ['base','point_of_sale'],
    
    'data': [
        'views/res_config_settings_inherit.xml',
    ],
    
    'assets': {
    'point_of_sale._assets_pos': [
        'hide_pos_cashcontrol_toggle/static/src/js/hide_cash_control_config.js',
    ],
},
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'auto_install': False,

}

