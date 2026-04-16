import logging
import pprint
import requests

from werkzeug import urls

from odoo.exceptions import UserError
from odoo import fields, models, api, _

from .. import const

_logger = logging.getLogger(__name__)


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    # Compago API key used to authenticate POS requests to the Compago API
    # This key can be obtained from the Compago administration panel
    compago_api_key = fields.Char(
        string='Compago API key',
        help='API key that authenticates Point of Sale requests to the Compago API. \n\n'
             'You can obtain this key from the Compago Admin Panel or by requesting it from your technical representative.\n\n'
             'To get the key from the Compago Admin Panel, follow these steps:\n'
             '1. Log in to your Compago account.\n'
             '2. Go to the "Settings" > "Developer" section.\n'
             '3. Generate a new API Key.',
        copy=False
    )

    # Environment selection for Compago API endpoints
    # Determines which API URL will be used for payment intent processing
    compago_environment = fields.Selection(
        [
            ('prod', 'Production'),
            ('demo', 'Demo'),
            ('local', 'Local')
        ],
        string='Compago Environment',
        default='prod',
        help='Select the environment that the Point of Sale will connect to::\n\n'
             '- Production: The environment for processing real payments with active terminals.\n\n'
             '- Demo: The environment for running tests or simulations; you will not receive real charges in your bank account.\n\n'
             '- Local: The environment for local development without any connection to Compago’s servers.'
    )

    compago_api_url = fields.Char(
        string='Compago API URL',
        default='http://host.docker.internal:8080'
    )

    compago_terminal_serial_number = fields.Char(
        string='Compago Terminal Serial Number',
        help='Serial number of the physical POS terminal',
        copy=False
    )

    compago_should_deep_link_to_app = fields.Boolean(
        string='Deep Link to Compago App',
        help='If enabled, the POS will attempt to open the payment processing app. This requires the app to be installed on the device.',
        default=True
    )

    @api.model
    def _load_pos_data_fields(self, config_id):
        params = super()._load_pos_data_fields(config_id)
        params += ['compago_should_deep_link_to_app']

        return params

    def _get_payment_terminal_selection(self):
        return super()._get_payment_terminal_selection() + [('compago', 'Compago')]

    def compago_create_payment_intent(self, data):
        """
        Creates a payment intent on Compago's API for card-present terminal transactions.

        Args:
            data (dict): Payment information containing:
                - amount: Transaction amount
                - currency: Currency code (e.g., 'MXN')
                - reference: External reference/order ID

        Returns:
            dict: API response containing the payment intent details
        """
        body = {
            'amount': data.get('amount'),
            'currency': data.get('currency'),
            'externalId': data.get('reference'),
            'terminalCode': self.sudo().compago_terminal_serial_number
        }

        # TODO: When the terminal is not found, we should display a better error to the user. Currently showing "404"
        response = self._compago_make_request('/api/payment-intent', payload=body, method='POST')

        _logger.debug('compago_create_payment_intent(), response from Compago: %s', response)
        return response

    def compago_cancel_payment_intent(self, payment_intent_id):
        """
        Cancels an existing payment intent on Compago's API.

        Args:
            payment_intent_id (str): The ID of the payment intent to cancel

        Returns:
            dict: API response confirming the cancellation
        """
        response = self._compago_make_request(f'/api/payment-intent/{payment_intent_id}/cancel', method='POST')

        _logger.debug('compago_cancel_payment_intent(), response from Compago: %s', response)
        return response

    def compago_get_payment_intent_status(self, payment_intent_id):
        """
        Retrieves the current status of a payment intent from Compago's API.

        Args:
            payment_intent_id (str): The ID of the payment intent to query

        Returns:
            dict: API response containing the payment intent status and details
        """
        response = self._compago_make_request(f'/api/payment-intent/{payment_intent_id}', method='GET')

        _logger.debug('compago_get_payment_intent_status(), response from Compago: %s', response)
        return response

    @api.constrains('use_payment_terminal')
    def _check_compago_terminal(self):
        if any(record.use_payment_terminal == 'compago' and record.company_id.currency_id.name != 'MXN' for record in
               self):
            raise UserError(_('This payment terminal can only be used with MXN currency.'))

    def _compago_get_api_url(self):
        """
        Returns the Compago API URL based on the selected environment.

        This method is the centralized place to determine which API endpoint
        should be used for all Compago payment intent requests in POS.

        Returns:
            str: The API URL corresponding to the selected environment
                 (Production, Demo, or Local)
        """
        self.ensure_one()

        # Get the environment setting from the payment method configuration
        environment = self.sudo().compago_environment

        # Return the appropriate API URL based on the selected environment
        if environment == 'prod':
            return const.PROD_API_URL
        elif environment == 'demo':
            return const.DEMO_API_URL
        else:
            return self.sudo().compago_api_url

    def _compago_make_request(self, endpoint, payload=None, method='POST'):
        """
        Makes an HTTP request to the Compago API with proper authentication and error handling.

        Args:
            endpoint (str): API endpoint path (e.g., '/api/payment-intent')
            payload (dict, optional): Request payload for POST requests or query params for GET
            method (str): HTTP method to use ('POST' or 'GET'). Defaults to 'POST'

        Returns:
            dict: JSON response from the API, or error dict with 'errorMessage' key if request fails
        """
        self.ensure_one()

        api_url = self._compago_get_api_url()
        url = urls.url_join(api_url, endpoint)
        headers = {'x-api-key': self.sudo().compago_api_key}

        try:
            if method == 'GET':
                response = requests.get(url, params=payload, headers=headers, timeout=10)
            else:
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                try:
                    response.raise_for_status()
                except requests.exceptions.HTTPError as error:
                    _logger.warning(
                        'Invalid API request at %s with data:\n%s\nError: %s', url, pprint.pformat(payload), error
                    )
                    return {'errorMessage': str(error)}
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as error:
            _logger.warning('Unable to reach endpoint at %s', url)
            return {'errorMessage': _('Could not establish the connection to the API. Error: %s') % error}

        return response.json()
