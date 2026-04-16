import json
import string
import base64
from datetime import datetime, timedelta
from random import choice

import requests
import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.image import image_data_uri

_logger = logging.getLogger(__name__)


def _rand_str(length):
    return ''.join(choice(string.ascii_uppercase + string.digits) for _ in range(length))


class PosPaymentMethod(models.Model):
    _inherit = "pos.payment.method"

    qr30_provider = fields.Selection(
        selection=lambda self: self.env['pos.bank'].get_bank_code(),
        string="Bank", default="014")
    qr30_biller_name = fields.Char(string="Name")
    qr30_biller_code = fields.Char(string="Biller ID")
    qr30_ref3_prefix = fields.Char(string="Ref 3 Prefix")

    qr30_api_key = fields.Char(string="API Key", groups='base.group_system')
    qr30_api_secret = fields.Char(string="API Secret", groups='base.group_system')
    qr30_api_auth_token = fields.Char(string="Auth Token", groups='base.group_system')
    qr30_api_auth_token_expire_time = fields.Datetime(default=fields.Datetime.now())
    qr30_api_base_url = fields.Char(
        string="Base url", groups='base.group_system', readonly=False, store=True,
        default="https://api-sandbox.partners.scb/partners/sandbox/v1")

    qr30_has_callback = fields.Boolean(string="Enable callback", default=True)
    qr30_callback_url = fields.Char(string="Callback URL",
                                    readonly=True,
                                    store=False,
                                    default=lambda self: f"{self.get_base_url()}/pos_qr/notification",
                                    groups='base.group_system')

    qr30_currency_id = fields.Many2one(
        related='company_id.currency_id',
        help="The main currency of the company, used to display monetary fields.",
    )
    qr30_minimum_price = fields.Monetary(
        string="Minimum Price",
        help="The minimum payment amount that this payment provider is available for.",
        currency_field='qr30_currency_id',
        default=0)
    qr30_maximum_price = fields.Monetary(
        string="Maximum Price",
        help="The maximum payment amount that this payment provider is available for. Leave 0.00 "
             "to make it available for any payment amount.",
        currency_field='qr30_currency_id',
        default=0)
    qr30_payment_fee = fields.Monetary(
        string="Customer Fee",
        help="The amount to add to the bill.",
        currency_field='qr30_currency_id',
        default=0)
    qr30_payment_fee_product_id = fields.Many2one('product.product', string="Fix Payment Product")

    qr30_payment_timer = fields.Integer(string='QR Timer(Seconds)', default=300)

    def _load_pos_data_fields(self, config_id):
        data = super()._load_pos_data_fields(config_id)
        data += ['qr_code_method', 'qr30_provider', 'qr30_biller_name', 'qr30_biller_code',
                 'qr30_payment_timer', 'qr30_payment_fee', 'qr30_payment_fee_product_id',
                 'qr30_minimum_price', 'qr30_maximum_price']
        return data

    @api.depends('payment_method_type')
    def _compute_hide_qr_code_method(self):
        for payment_method in self:
            payment_method.hide_qr_code_method = payment_method.payment_method_type != 'qr_code'

    @api.depends('payment_method_type', 'journal_id')
    def _compute_qr(self):
        for pm in self:
            if pm.payment_method_type != "qr_code" or pm.qr_code_method == "qr30":
                pm.default_qr = False
                continue
            try:
                # Generate QR without amount that can then be used when the POS is offline
                pm.default_qr = pm.get_qr_code(False, '', '', pm.company_id.currency_id.id, False)
            except UserError:
                pm.default_qr = False

    @api.onchange('payment_method_type')
    def _onchange_payment_method_type(self):
        super()._onchange_payment_method_type()

        if self.payment_method_type != 'qr_code':
            self.qr_code_method = None

    @api.onchange('is_online_payment')
    def _onchange_is_online_payment(self):
        # Unset the use_payment_terminal field when switching to a payment method that doesn't use it
        if self.is_online_payment:
            self.payment_method_type = 'none'

    def _is_write_forbidden(self, fields):
        return super(PosPaymentMethod, self)._is_write_forbidden(fields -
                                                                 {'qr30_api_auth_token', 'qr30_api_auth_token_expire_time'})

    def get_qr_code(
            self, amount, free_communication, structured_communication, currency, debtor_partner):
        self.ensure_one()

        if self.qr_code_method != "qr30":
            return super().get_qr_code(amount, free_communication, structured_communication, currency, debtor_partner)

        if 0 < self.qr30_minimum_price and amount < self.qr30_minimum_price:
            raise UserError(
                _("Amount is not in the range of this payment method (Minimum = %f)", self.qr30_minimum_price))

        if 0 < self.qr30_maximum_price < amount:
            raise UserError(
                _("Amount is not in the range of this payment method (Maximum = %f)", self.qr30_maximum_price))

        ref1 = _rand_str(20)
        ref2 = _rand_str(20)
        ref3 = f"{self.qr30_ref3_prefix}{_rand_str(7)}"

        qr30_data = self._call_qr30_api(amount, ref1, ref2, ref3)
        barcode = self.env['ir.actions.report'].barcode(barcode_type='QR',
                                                        value=qr30_data,
                                                        height=350,
                                                        width=350)
        qr_code_image = image_data_uri(base64.b64encode(barcode))

        if qr_code_image:
            return {
                'qrImage': qr_code_image,
                'qrRawData': qr30_data,
                'amount': amount,
                'ref1': ref1,
                'ref2': ref2,
                'ref3': ref3,
            }
        raise UserError(_("Bank QR generation failed for this payment method"))

    def _call_qr30_api(self, amount, ref1, ref2, ref3):
        """ Generates and returns a QR-code
        """
        _logger.info("Getting qr")

        url = f"{self.qr30_api_base_url}/payment/qrcode/create"

        token = self._get_auth_token()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "resourceOwnerId": self.qr30_api_key,
            "requestUId": str(self.env.user.id),
            "accept-language": "EN",
        }

        json_data = {
            "qrType": "PP",
            "ppType": "BILLERID",
            "amount": str(amount),
            "ppId": self.qr30_biller_code,
            "ref1": ref1,
            "ref2": ref2,
            "ref3": ref3,
        }

        _logger.debug(headers)
        _logger.info(json_data)

        try:
            response = requests.post(url, data=json.dumps(json_data), headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.HTTPError as err:
            raise ValidationError(
                _("Communication with SCB failed. SCB returned with the following error: %s", err))
        except (requests.RequestException, ValueError):
            raise ValidationError(_("Could not establish a connection to the SCB API."))
        except requests.JSONDecodeError:
            raise ValidationError(_("Could not decode response."))

        if response.status_code != 200:
            raise ValidationError(_("Could not decode response."))

        if not data.get('data'):
            raise ValidationError(_("Could not decode response."))

        if not data.get('data').get('qrRawData'):
            raise ValidationError(_("Could not decode response."))

        return data.get('data').get('qrRawData')

    def _get_auth_token(self):
        self.ensure_one()

        if fields.Datetime.now() >= self.qr30_api_auth_token_expire_time:
            _logger.info("Auth token expired")
            token, expires_time = self._call_auth_api()
            self.qr30_api_auth_token = token
            # add 120 seconds buffer before the token expires
            self.qr30_api_auth_token_expire_time = datetime.fromtimestamp(expires_time - 120)

        return self.qr30_api_auth_token

    def _call_auth_api(self):
        _logger.info("Getting new auth token")

        url = f"{self.qr30_api_base_url}/oauth/token"

        headers = {
            "Content-Type": "application/json",
            "resourceOwnerId": self.qr30_api_key,
            "requestUId": str(self.env.user.id),
            "accept-language": "EN",
        }

        json_data = {
            "applicationKey": self.qr30_api_key,
            "applicationSecret": self.qr30_api_secret,
        }

        try:
            response = requests.post(url, data=json.dumps(json_data), headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.HTTPError as err:
            raise ValidationError(
                _(
                    "Communication with %s failed. %s returned with the following error: %s",
                    self.qr30_provider, self.qr30_provider, err))
        except (requests.RequestException, ValueError):
            raise ValidationError(
                _("Could not establish a connection to the %s API.", self.qr30_provider))
        except requests.JSONDecodeError:
            raise ValidationError(_("Could not decode response."))

        if response.status_code != 200:
            raise ValidationError(_("Could not decode response."))

        if not data.get('data'):
            raise ValidationError(_("Could not decode response."))

        token = data.get('data').get('accessToken')
        expires_time = data.get('data').get('expiresAt')

        if not token or not expires_time:
            raise ValidationError(_("Could not decode response."))

        return (token, expires_time)

    def action_test_connection(self):
        try:
            result = self._call_auth_api()
            if result:
                message = _('Connection Test Successful!')
            else:
                message = _('Connection Test No Message!')
        except Exception as e:
            message = str(_(e)) if e else _("Something went wrong, please try again")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': message,
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }

    @api.model
    def void_qr_code(self):
        print("\nCall Void QR Code")
