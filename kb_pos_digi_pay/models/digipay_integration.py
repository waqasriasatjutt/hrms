# -*- coding: utf-8 -*-

from odoo import api, models, fields
import json
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError
from odoo.tools.translate import _
import requests
import logging

import qrcode
import base64
from io import StringIO, BytesIO
from PIL import Image
from odoo.tools.misc import file_path
from pytz import timezone

_logger = logging.getLogger(__name__)


class DigiPayIntegration(models.TransientModel):
    _name = "digi.pay.integration"
    _description = 'DigiPay integration'

    # Create Order to DigiPay
    @api.model
    def create_invoice(self, order_name, config_id, amount=0, session_id='-'):
        _logger.info("---- DigiPay create invoice, %s, %s, %s, %s" % (order_name, config_id, amount, session_id))
        pos_config = self.env['pos.config'].browse(config_id)
        digipay_ecommerce_token, test_mode_on = self._get_digipay_token(pos_config)
        if digipay_ecommerce_token:
            if amount <= 0:
                return {
                    'status': 'ng',
                    'code': '-',
                    'body': 'Must be transaction amount > 0 !'
                }
            headers = {'Content-Type': 'application/json'}
            body = {
                "ecommerce_token": digipay_ecommerce_token,
                "amount": amount * 100,
            }
            try:
                invoice_base_url = self._convert_url(self.env.company.digipay_invoice_create_url, test_mode_on)
                response = requests.post(invoice_base_url, headers=headers, data=json.dumps(body))
                if response.status_code == 200:
                    response_data = response.json()
                    if response_data.get('status_code', 'ng') == 'ok':
                        _logger.info("---- DigiPay create invoice, response success %s" % (response_data))
                        qr_data = response_data.get('ret', {}).get('order_id')
                        qr_image = self._qr_generate(qr_data)
                        invoice_id = qr_data.split('/')[-1]
                        return {
                            'status': 'ok',
                            'qr_data': qr_image, 
                            'invoice_id': invoice_id}
                    else:
                        return {
                            'status': 'ng',
                            'code': response_data.get('msg', {}).get('code'),
                            'body': response_data.get('msg', {}).get('body')
                        }
                else:
                    print("====response", body, response.status_code, response.text)
                    _logger.info("---- DigiPay create invoice, response failed \n%s" % (response.json()))
                    raise UserError(_('DigiPay invoice create error! code: %s, message: %r' % (response.status_code, response.json()['msg'])))
            except requests.ConnectionError:
                raise UserError(_('DigiPay Invoice create connection error!'))
        else:
            # raise UserError(_('Please set DigiPay Ecommerce token!'))
            return {
                'status': 'ng',
                'code': '-',
                'body': 'Please set DigiPay Ecommerce token!'
            }

    # Success response
    # {
    #     'status_code': 'ok', 
    #     'ret': {
    #         'shop': 'САМЪЯАХИЙД', 
    #         'amount': '7880.0', 
    #         'order_id': 'http://pass.mn/order/d9daae41f15543fab8c9b3b28abcb078', 
    #         'order_ttl': 600, 
    #         'db_ref_no': '20240115172354904'
    #     }
    # } 

    @api.model
    def check_invoice(self, config_id, invoice_id):
        _logger.info("---- DigiPay check_invoice, request %s, %s" % (config_id, invoice_id))
        pos_config = self.env['pos.config'].browse(config_id)
        digipay_ecommerce_token, test_mode_on = self._get_digipay_token(pos_config)
        if digipay_ecommerce_token:
            headers = {'Content-Type': 'application/json'}
            body = {
                "ecommerce_token": digipay_ecommerce_token,
                "order_id": invoice_id,
            }
            try:
                check_invoice_base_url = self._convert_url(self.env.company.digipay_invoice_check_url, test_mode_on)
                response = requests.post(check_invoice_base_url, headers=headers, data=json.dumps(body),
                                         verify=True)
                if response.status_code == 200:
                    response_data = response.json()
                    if response_data.get('status_code', 'ng') == 'ok':
                        _logger.info("---- DigiPay check_invoice, response paid %s" % (response_data))
                        status = response_data.get('ret', {}).get('status')
                        status_text = response_data.get('ret', {}).get('status_text')
                        return {
                            'invoice_id': invoice_id,
                            'msg': status_text, 
                            'status': status,
                            'ret': response_data.get('ret', {}),
                        }
                    else:
                        _logger.info("---- DigiPay check_invoice, response unpiad %s" % (response_data))
                        return {
                            'status': 'ng',
                            'code': response_data.get('msg', {}).get('code'),
                            'body': response_data.get('msg', {}).get('body')
                        }
                else:
                    raise UserError(_('DigiPay check_invoice error! code: %s, message: %s' % (
                    response.status_code, response.json()['message'])))
            except requests.ConnectionError:
                raise UserError(_('DigiPay check_invoice connection error!'))
        else:
            return {
                'status': 'ng',
                'code': '-',
                'body': 'Please set DigiPay Ecommerce token!'
            }

    # Cancel Order to DIGI PAY
    @api.model
    def cancel_invoice(self, config_id, invoice_id):
        _logger.info("---- DigiPay cancel_invoice data: %s %s" % (config_id, invoice_id))
        pos_config = self.env['pos.config'].browse(config_id)
        digipay_ecommerce_token, test_mode_on = self._get_digipay_token(pos_config)
        if digipay_ecommerce_token:
            headers = {'Content-Type': 'application/json'}
            body = {
                "ecommerce_token": digipay_ecommerce_token,
                "order_id": invoice_id,
            }
            try:
                cancel_invoice_base_url = self._convert_url(self.env.company.digipay_invoice_cancel_url, test_mode_on)
                response = requests.post(cancel_invoice_base_url, headers=headers, data=json.dumps(body),
                                         verify=True)
                if response.status_code == 200:
                    response_data = response.json()
                    if response_data.get('status_code', 'ng') == 'ok':
                        _logger.info("---- DigiPay cancel_invoice, response cancel %s" % (response_data))
                        status = response_data.get('ret', {}).get('status')
                        status_text = response_data.get('ret', {}).get('status_text', 'Cancelled')
                        return {
                            'msg': status_text, 
                            'status': status
                        }
                    else:
                        _logger.info("---- DigiPay cancel_invoice, response unpiad %s" % (response_data))
                        return {
                            'status': 'ng',
                            'code': response_data.get('msg', {}).get('code'),
                            'body': response_data.get('msg', {}).get('body')
                        }
                else:
                    raise UserError(_('DigiPay cancel_invoice error! code: %s, message: %s' % (
                    response.status_code, response.json()['message'])))
            except requests.ConnectionError:
                raise UserError(_('DigiPay cancel_invoice connection error!'))
        else:
            return {
                'status': 'ng',
                'code': '-',
                'body': 'Please set DigiPay Ecommerce token!'
            }

    # Resp
    # {
    #    "status_code":"ng",
    #    "ret":"None",
    #    "msg":{
    #       "code":"EC15",
    #       "level":"4",
    #       "body":"Order cannot be cancelled, status is 'expired'."
    #    }
    # }


    # DIGI PAY settlement
    @api.model
    def settlement_digipay(self, config_id, session_id, date_start=False, date_end=False):
        _logger.info("---- DigiPay settlement data: %s %s %s->%s" % (config_id, session_id, date_start, date_end))
        pos_config = self.env['pos.config'].browse(config_id)
        pos_session = self.env['pos.session'].browse(session_id)
        digipay_ecommerce_token, test_mode_on = self._get_digipay_token(pos_config)
        if digipay_ecommerce_token:
            if not date_start or not date_end:
                date_start = pos_session.start_at
                date_end = pos_session.stop_at
            # USER TIMEZONE
            user_tz = self.env.user.tz
            date_start = date_start.astimezone(timezone(user_tz))
            date_end = date_end.astimezone(timezone(user_tz))

            headers = {'Content-Type': 'application/json'}
            body = {
                "ecommerce_token": digipay_ecommerce_token,
                "start_datetime": date_start.strftime("%Y-%m-%d %H:%M:%S"),
                "end_datetime": date_end.strftime("%Y-%m-%d %H:%M:%S"),
            }
            try:
                settlement_base_url = self._convert_url(self.env.company.digipay_settlement_url, test_mode_on)
                response = requests.post(settlement_base_url, headers=headers, data=json.dumps(body),
                                         verify=True)
                if response.status_code == 200:
                    response_data = response.json()
                    if response_data.get('status_code', 'ng') == 'ok':
                        _logger.info("---- DigiPay settlement, response: %s" % (response_data))
                        status = response_data.get('ret', {}).get('resp_code')
                        status_text = response_data.get('ret', {}).get('resp_msg', 'Default settlement text')
                        sale_count = response_data.get('ret', {}).get('sale_count', 0)
                        sale_total = response_data.get('ret', {}).get('sale_total', 0)
                        void_count = response_data.get('ret', {}).get('void_count', 0)
                        void_total = response_data.get('ret', {}).get('void_total', 0)
                        # Save
                        pos_session.digipay_description = status_text
                        pos_session.digipay_sale_count = sale_count
                        pos_session.digipay_sale_total = sale_total
                        pos_session.digipay_void_count = void_count
                        pos_session.digipay_void_total = void_total
                        return {
                            'msg': status_text, 
                            'status': status,
                            'sale_count': sale_count,
                            'sale_total': sale_total,
                            'void_count': void_count,
                            'void_total': void_total,
                        }
                    else:
                        _logger.info("---- DigiPay settlement, response: %s" % (response_data))
                        pos_session.digipay_description = response_data.get('msg', {}).get('body')
                        return {
                            'status': 'ng',
                            'code': response_data.get('msg', {}).get('code'),
                            'body': response_data.get('msg', {}).get('body')
                        }
                else:
                    pos_session.digipay_description = response.json()['message']
                    # raise UserError(_('DigiPay settlement error! code: %s, message: %s' % (
                    # response.status_code, response.json()['message'])))
            except requests.ConnectionError:
                pos_session.digipay_description = "DigiPay settlement connection error"
                # raise UserError(_('DigiPay settlement connection error!'))
        else:
            pos_session.digipay_description
            return {
                'status': 'ng',
                'code': '-',
                'body': 'Please set DigiPay Ecommerce token!'
            }


    # GET pass token
    def _get_digipay_token(self, pos_config):
        payment_method = self.env['pos.payment.method'].sudo().search([
            ('use_payment_terminal','=','digi_pay'),
            ('is_digipay_test_mode','=',True)], limit=1)
        if payment_method and payment_method.is_digipay_test_mode:
            _logger.info("---- DigiPay _get_digipay_token TEST mode is '%s'" % (payment_method.is_digipay_test_mode))
            # This token only TEST token !!!!!!!!!!!!
            return 'b2a1acfc5e6e49ad88a7784241d2d1f1', payment_method.is_digipay_test_mode
        else:
            return pos_config.digipay_ecommerce_token, False

    def _convert_url(self, url, test_mode_on):
        if test_mode_on:
            url = url.replace('ecom.pass', 'ecomstg.pass')
        return url

    def _qr_generate(self, data):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=0,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#010101", back_color="white")
        # Logo
        path = file_path('kb_pos_digi_pay/static/description/icon3.png')
        logo = Image.open(path)
        # logo = logo.resize((40, 40), Image.ANTIALIAS)
        qr_img_size = img.size
        logo_position = (
            (qr_img_size[0] - 40) // 2,
            (qr_img_size[1] - 40) // 2,
        )
        # Paste the logo on the QR code
        img.paste(logo, logo_position)
        # Save
        buffered = BytesIO()
        img.save(buffered)
        img_str = base64.b64encode(buffered.getvalue())
        return img_str