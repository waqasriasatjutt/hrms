# -*- coding: utf-8 -*-
########################################################################################
#                       ЭЗЭМШИГЧИЙН ЭРХ (C) "ДАТАБЭЙНК" ХХК                            #
#                                                                                      #
#    БҮХ ЭРХ ХУУЛИАР ХАМГААЛАГДСАН БОЛНО. ЭНЭХҮҮ ПРОГРАМ НЬ "ДАТАБЭЙНК" ХХК-ИЙН ӨМЧ    #
#     БӨГӨӨД ГАГЦХҮҮ "ДАТАБЭЙНК" ХХК-ИЙН ХЭРЭГЦЭЭНД ХЭРЭГЛЭГДЭХ БОЛНО. ПРОГРАММЫН      #
#       ЯМАР Ч ХЭСГИЙГ "ДАТАБЭЙНК" ХХК-ИЙН УРЬДЧИЛАН ОЛГОСОН ЗӨВШӨӨРӨЛГҮЙГЭЭР          #
#             ХУУЛБАРЛАХ ЭСВЭЛ БУСДАД ЗАДРУУЛАХ, ТҮГЭЭХИЙГ ХОРИГЛОНО.                  #
#                                                                                      #
#                              "ДАТАБЭЙНК" ХХК-ИЙН ӨМЧ                                 #
#                                                                                      #
#  ----------------------------------------------------------------------------------  #
#                                                                                      #
#                     DATABANK LLC CONFIDENTIAL AND PROPRIETARY                        #
#                                                                                      #
#                     COPYRIGHT (C) DATABANK LLC since 2017                            #
#                                                                                      #
#      ALL RIGHTS RESERVED BY DATABANK LLC.  THIS PROGRAM MUST BE                      #
#    USED SOLELY FOR THE PURPOSE FOR WHICH IT WAS FURNISHED BY DATABANK LLC.           #
#   NO PART OF THIS PROGRAM MAY BE REPRODUCED OR DISCLOSED TO OTHERS, IN ANY           #
#        FORM, WITHOUT THE PRIOR WRITTEN PERMISSION OF DATABANK LLC.                   #
#                                                                                      #
#     USE OF COPYRIGHT NOTICE DOES NOT EVIDENCE PUBLICATION OF THE PROGRAM.            #
#                                                                                      #
#                     DATABANK LLC CONFIDENTIAL AND PROPRIETARY                        #
#                                                                                      #
########################################################################################

{
    'name': 'DigiPay POS payment',
    'version': '1.0.1',
    'author': 'DATABANK LLC',
    'website': 'https://www.khanbank.com/',
    'images': ["static/img/app_banner.png"],
    'category': 'Sales/Point of Sale',
    'sequence': 6,
    'description': 'Integrate your POS with an DigiPay method.',
    'summary': 'Integrate your POS with an DigiPay method detailed',
    'data': [
        'security/ir.model.access.csv',
        'data/digi_payment_method_data.xml',
        'views/res_config_settings_views.xml',
        'views/pos_payment_method_inherit_view.xml',
        # 'views/pos_inherit_assets_view.xml',
    ],
    'depends': ['point_of_sale'],
    'installable': True,
    'auto_install': False,
    'assets': {
        'point_of_sale._assets_pos': [
            "kb_pos_digi_pay/static/src/app/payment_digi_pay.js",
            "kb_pos_digi_pay/static/src/app/digi_qr_popup.js",
            "kb_pos_digi_pay/static/src/overrides/models/models.js",
            "kb_pos_digi_pay/static/src/xml/digi_qr_popup.xml",
        ],
        'web.assets_qweb': [
            'kb_pos_digi_pay/static/src/xml/digi_qr_popup.xml',
        ],
    },
    'license': 'GPL-3',
    'price': 0, 
}
