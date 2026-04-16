# -*- coding: utf-8 -*-
# from odoo import http


# class LealRedeem(http.Controller):
#     @http.route('/leal_redeem/leal_redeem', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/leal_redeem/leal_redeem/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('leal_redeem.listing', {
#             'root': '/leal_redeem/leal_redeem',
#             'objects': http.request.env['leal_redeem.leal_redeem'].search([]),
#         })

#     @http.route('/leal_redeem/leal_redeem/objects/<model("leal_redeem.leal_redeem"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('leal_redeem.object', {
#             'object': obj
#         })

