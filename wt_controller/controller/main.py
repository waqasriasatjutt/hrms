from odoo import http
from odoo.http import request
import time
import requests
import json
import hashlib
import os
import werkzeug.wrappers
import datetime
import json
from odoo import http
from odoo.http import request
from odoo.http import route
# import numpy as np
# import base64
from odoo.exceptions import AccessError, UserError, AccessDenied


import odoo
# import boto3

# import jwt



class Main(http.Controller):


    @http.route('/api/products', type='json', auth='public', cors='*', methods=['POST'])
    def api_products_list(self, **kwargs):
        """
        Odoo SOP compliant product exposure endpoint
        """

        env = request.env

        # 🔹 Use public user but controlled sudo
        Product = env['product.product'].with_context(
            lang=env.lang,
            company_id=env.company.id,
            allowed_company_ids=[env.company.id],
        ).sudo()

        domain = [
            ('active', '=', True),
            ('sale_ok', '=', True),
        ]

        # 🔹 Pagination (Odoo standard)
        limit = int(kwargs.get('limit', 50))
        offset = int(kwargs.get('offset', 0))

        products = Product.search(domain, limit=limit, offset=offset)

        # 🔹 Pricelist handling (ODOO SOP)
        pricelist = env['product.pricelist'].sudo().search(
            [('company_id', 'in', [env.company.id, False])],
            limit=1
        )

        products = products.with_context(pricelist=pricelist.id)

        result = []
        for product in products:
            result.append({
                'id': product.id,
                'template_id': product.product_tmpl_id.id,
                'name': product.display_name,
                'price': product.lst_price,
                'currency': pricelist.currency_id.name,
                'default_code': product.default_code,
                'uom': product.uom_id.name,
                'category': product.categ_id.name,
            })

        return {
            'status': 200,
            'count': len(result),
            'products': result,
        }

    # def generate_jwt(self, user_id):
    #     # encoded_jwt = jwt.encode({"user_id": user_id,"timestamp": time.time()}, "secret", algorithm="HS256")
    #     encoded_jwt = jwt.encode({"user_id": user_id}, "secret", algorithm="HS256")
    #     print(encoded_jwt)
    #     token = jwt.decode(encoded_jwt, "secret", algorithms=["HS256"])
    #     users = request.env['res.users'].sudo().search([('id','=', user_id)])
    #     for user in users:
    #         if user.token_for_sale_person:
    #             return user.token_for_sale_person
    #         else:
    #             user.token_for_sale_person = encoded_jwt
    #             return user.token_for_sale_person



    def unique(list1):

        # intilize a null list
        unique_list = []

        # traverse for all elements
        for x in list1:
            # check if exists in unique_list or not
            if x not in unique_list:
                unique_list.append(x)
        # print list
        for x in unique_list:
            print
            x,


    # @http.route('/get_boto', auth='public', type='json', methods=['POST'], cors='*')
    # def get_boto(self):
    #     s3 = boto3.resource('s3',
    #                         endpoint_url='https://s3.ap-southeast-1.wasabisys.com',
    #                         aws_access_key_id='NBGRLBQU4YR8VL4O9EP3',
    #                         aws_secret_access_key='rRp6qA3WJtVBnn7r3F8psja9dBBWbDXlOANYC3Xn'
    #                         )
    #     boto_test_bucket = s3.Bucket('odoo-users')

    #     with open("/mnt/extra-addons/distribution_app_apis/upload-test.txt", "w") as outfile:
    #         outfile.write("Hello S3!")

    #     # Upload the file. "MyDirectory/test.txt" is the name of the object to create

    #     url_1 = boto_test_bucket.upload_file("/mnt/extra-addons/distribution_app_apis/upload-test.txt", "MyDirectory/test.txt")
    #     return {
    #         'masg':"aaaaaaa",
    #         'res': s3,
    #         'bucket': boto_test_bucket,
    #         'url': url_1
    #     }


    # @http.route('/login_user_api', auth='public', type='json', methods=['POST'], cors='*')
    # def login_user(self, login, password):
    #     responce_value = {}
    #     email = request.env['res.users'].sudo().search([('phone', '=', login), ('user_pin', '=', password)])
    #     # password = request.env['res.users'].sudo().search([('user_pin', '=', password)])
    #     # request.env.cr.execute("""
    #     #                     select password as passw, login
    #     #                     from res_users as ru
    #     #                     where ru.login = %s
    #     #                     group by ru.password, ru.login""",
    #     #                     (email.login,))
    #     # sal = request.env.cr.fetchall()

    #     try:
    #         # uid = request.session.authenticate(request.session.db, email.login, email.password)
    #         responce_value = "200"

    #         encoded_jwt = jwt.encode({"user_id": str(email.login),"password": str(email.user_pin)}, "secret", algorithm="HS256")
    #         # token = jwt.decode(encoded_jwt, "secret", algorithms=["HS256"])
    #         users = request.env['res.users'].sudo().search([('login', '=', email.login)])
    #         for user in users:
    #             if user.token_for_sale_person:
    #                 token = user.token_for_sale_person
    #             else:
    #                 user.sudo().write({'token_for_sale_person': encoded_jwt});
    #                 token = user.token_for_sale_person
    #         status = 200
    #         user = request.env['res.users'].sudo().search([('id', '=', users.id)])
    #         # responce_value = []
    #         responce_value = {
    #                              'status': 200,
    #                              'msg': 'logined sucessfully',
    #                              'user_login': user.login,
    #                              'user_account': user.phone,
    #                              'user_id': user.id,
    #                              'user_name': user.name,
    #                              'token': token,
    #         }
    #     except:
    #         responce_value = {
    #                 'status': 201,
    #                 'msg': 'Access Denied',
    #                 'user': email.login,
    #                 'userp': email.user_pin,
    #                 'msg': 'Access Denied',
    #             }

    #     return responce_value


    # @http.route('/login_via_token', auth='public', type='json', methods=['POST'], cors='*')
    # def login_via_token(self, token):
    #     user = request.env['res.users'].sudo().search([('token_for_sale_person', '=', token)])
    #     token_vals = jwt.decode(token, "secret", algorithms=["HS256"])
    #     if user:
    #         try:
    #             uid = request.session.authenticate(request.session.db, token_vals['user_id'], token_vals['password'])
    #             responce_value = "200"
    #             status = 200
    #             user = request.env['res.users'].sudo().search([('id', '=', uid)])
    #             # responce_value = []
    #             responce_value = {
    #                                  'status': 200,
    #                                  'msg': 'logined sucessfully',
    #                                  'user_login': user.login,
    #                                  'user_id': user.id,
    #                                  'user_name': user.name,
    #                                  'token': token,
    #             }
    #         except:
    #             responce_value = {
    #                     'status': 201,
    #                     'msg': 'Access Denied',
    #                     'login': token_vals['user_id'],
    #                     'password': token_vals,
    #                 }
    #     else:
    #         responce_value = {
    #             'status': 201,
    #             'msg': 'Access Denied Authenticate Again',
    #         }

    #     return responce_value


    @http.route('/products', type='json', auth='public', cors='*')
    def products_list(self):
        # user = request.env['res.users'].sudo().search([('token_for_sale_person', '=', token)])
        # # token_vals = jwt.decode(token, "secret", algorithms=["HS256"])
        # if user:
        products = request.env['product.template'].sudo().search(
            [('active', '=', True)])

        res = []
        for product in products:

            res.append({
                'id': product.product_variant_id.id,
                'search_id': product.id,
                'name': product.display_name,
                'price': product.list_price,
                'currency': product.currency_id.name,
                'notes': product.default_code,
                'description': product.description,
                'product_category': product.categ_id.name,
                'uom': product.uom_id.name,
                'product_category_id': product.categ_id.id,
            })

        return {
            'status': 200,
            'msg': 'Fetched All Products',
            'products': res,
        }
    # else:
    #     return {
    #         'status': 2001,
    #         'msg': 'Access Denied',
    #     }


