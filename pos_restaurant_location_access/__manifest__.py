# -*- coding: utf-8 -*-
# Part of Warlock Technologies Pvt. Ltd. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name':'pos restaurant location access',
    'version':'18.0.0.1',
    'summary':'pos restaurant location access',
    'description':'Employee can access only own floors',
    'author': 'Warlock Technologies Pvt Ltd.',
    'category':'Point Of Sale',
    'website': 'https://www.warlocktechnologies.com',
    'depends':['point_of_sale','hr','pos_hr','pos_restaurant'],
    'data':[
        "views/views.xml",
    ],
    'assets':{
        'point_of_sale._assets_pos': [
            "/pos_restaurant_location_access/static/src/apps/floor_screen/floor_screen.js",
            "/pos_restaurant_location_access/static/src/apps/floor_screen/floor_screen.xml",
        ],
    },
    'external_dependencies': {
    },
    'images':['static/images/screen_image.png'],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
}
