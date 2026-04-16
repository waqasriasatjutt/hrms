# -*- coding: utf-8 -*-
#################################################################################
# Author      : HSxTECH (<https://hsxtech.net/>)
# Copyright(c): 2024-Present HSxTECH
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://hsxtech.net/license.html/>
#################################################################################
{
    "name": "Address AutoComplete for POS + Contacts",
    "summary": """
                            The HSxTECH Address Autocomplete module utilizes the Google API to identify customers' complete addresses and automatically inputs them into various fields in both Contacts and Point of Sale applications.
                            """,
    "category": "Point Of Sale",
    "version": "1.0.0",
    "author": "HSxTECH",
    "license": "LGPL-3",
    "website": "https://hsxtech.net",
    "description": """
                            The HSxTECH Address Autocomplete module utilizes the Google API to identify customers' complete addresses and input them into fields like street, city, and country in both Contacts and Point of Sale applications, saving time and cost while reducing human errors.
                            """,
    "depends": ['base_setup', 'point_of_sale', 'contacts'],
    "data": ['views/res_config_settings_views.xml'],
    "assets": {
        'web.assets_backend': [
            '/hs_autocomplete_address/static/src/css/auto.css',
            '/hs_autocomplete_address/static/src/xml/autocomplete.xml',
            '/hs_autocomplete_address/static/src/js/backend_address.js',
        ],
        'point_of_sale._assets_pos': [
            '/hs_autocomplete_address/static/src/css/auto.css',
            '/hs_autocomplete_address/static/src/xml/autocomplete.xml',
            '/hs_autocomplete_address/static/src/js/pos_address.js',
        ],
    },
    "application": True,
    "installable": True,
    "auto_install": False,
    "pre_init_hook": "pre_init_check",
    "images":
        [
            'static/description/banner.gif',
            'static/description/icon.png',
        ],
}
