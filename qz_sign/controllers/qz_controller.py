# /odoo/custom_addons/qz_sign/controllers/qz_controller.py

from odoo import http
from odoo.http import request
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

class QZController(http.Controller):

    @http.route('/qz/sign', type='http', auth='public', cors='*')
    def sign(self, **kwargs):
        to_sign = kwargs.get('request')
        if not to_sign:
            return "Missing request parameter", 400

        key_path = '/opt/qz/private-key.pem'
        with open(key_path, 'rb') as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None)

        signature = private_key.sign(
            to_sign.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA512()
        )

        return base64.b64encode(signature)
