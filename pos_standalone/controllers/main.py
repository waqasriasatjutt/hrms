# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class PosStandaloneController(http.Controller):

    @http.route('/pos_standalone', type='http', auth='user', website=True)
    def index(self, **kwargs):
        """Main POS Standalone page"""
        return request.render('pos_standalone.index', {
            'title': 'POS Standalone',
        })

    @http.route('/pos_standalone/download', type='http', auth='user')
    def download_standalone(self, **kwargs):
        """Download standalone HTML file"""
        # Read the index.html file
        file_path = http.addons_manifest['pos_standalone']['addons_path'] + '/pos_standalone/static/index.html'
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return request.make_response(
                content,
                headers=[
                    ('Content-Type', 'text/html; charset=utf-8'),
                    ('Content-Disposition', 'attachment; filename=pos_standalone.html'),
                ]
            )
        except Exception as e:
            return request.make_response(
                f'Error downloading file: {str(e)}',
                headers=[('Content-Type', 'text/plain')],
                status=500
            )
