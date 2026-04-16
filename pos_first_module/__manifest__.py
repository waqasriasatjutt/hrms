{
    'name'              : 'Noorina',
    'version'           : '1.0',
    'author'            : 'Abhishek Dubey',
    'description'       : 'An App to show the customize message in the POS Screen',
    'category'          : 'Point of Sale',
    'summary'           : 'An App to show the customize message in the POS Screen',
    'depends'           : ['point_of_sale'],   
    'assets'            : {
                                'point_of_sale._assets_pos': [
                                    'pos_first_module/static/screens/*',
                                ],
                            },
    'license'           : 'LGPL-3',
    'installable'       : True,
    'application'       : True,
    'auto_install'      : False,
    'images'            : ['static/description/banner.png'],
}