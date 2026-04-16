# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import re

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class PosUnicobrosWebhook(http.Controller):
    @http.route('/unicobros/notification', methods=['POST'], type="http", auth="none", csrf=False)
    def notification(self):
        """ Process the notification sent by Unicobros POS.

        Notification format is always json
        """

        # Check for payload
        data = request.httprequest.get_json(silent=True)
        if not data:
            _logger.warning('POST message received with no data')
            return http.Response(status=400)
        _logger.warning('000000000000000000000 - POST message received: %s', data)

        # If and only if this webhook is related with a payment intend (see payment_unicobros.js)
        # then the field data['data']['payment']['reference'] contains a string
        # formated like `XXX_YYY_ZZZ` where:
        # - `XXX` is the session_id
        # - `YYY` is the payment_method_id
        # - `ZZZ` is the pos order uuid for customer identification (Format xxxx-xxxx-xxx) where x is a hexadecimal digit
        external_reference = data.get('data', {}).get('payment', {}).get('reference')

        unicobros_pattern = r'(\d+)_(\d+)_([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'

        if not external_reference or not (match := re.fullmatch(unicobros_pattern, external_reference)):
            _logger.warning('POST message received with no or malformed "external_reference" key: %s', external_reference)
            return http.Response(status=400)

        session_id, payment_method_id, _ = match.groups()

        pos_session_sudo = request.env['pos.session'].sudo().browse(int(session_id))
        if not pos_session_sudo or pos_session_sudo.state != 'opened':
            _logger.error("Invalid session id: %s", session_id)
            # This error is not related with Mercado Pago, simply acknowledge Mercado Pago message
            return http.Response('OK', status=200)

        payment_method_sudo = pos_session_sudo.config_id.payment_method_ids.filtered(lambda p: p.id == int(payment_method_id))
        if not payment_method_sudo or payment_method_sudo.use_payment_terminal != 'unicobros':
            _logger.error("Invalid payment method id: %s", payment_method_id)
            # This error is not related with Unicobros, simply acknowledge Unicobros message
            return http.Response('OK', status=200)
        
        # We have to check if this comes from Unicobros with id device
        device_reference = data.get('data', {}).get('pos', {}).get('terminal', {}).get('reference')
        if not device_reference or device_reference != payment_method_sudo.uni_id_point_smart:
            _logger.error("Invalid device reference id: %s", device_reference)
            # This error is not related with Unicobros, simply acknowledge Unicobros message
            return http.Response('OK', status=200)
        
        # Notify the frontend that we received a message from Unicobros
        pos_session_sudo.config_id._notify('UNICOBROS_LATEST_MESSAGE', {
            'config_id': pos_session_sudo.config_id.id,
            'payment_mode_unicobros': data.get('data', {}).get('payment', {}).get('source', {}).get('type', 'Unknown'),
            'card_brand_unicobros': data.get('data', {}).get('payment', {}).get('source', {}).get('name', 'Unknown'),
            'card_no_unicobros': data.get('data', {}).get('payment', {}).get('source', {}).get('number', '0000'),
            'cardholder_name_unicobros': data.get('data', {}).get('payment', {}).get('source', {}).get('cardholder', {}).get('name', 'Unknown'),
            'status_payment_unicobros': data.get('data', {}).get('payment', {}).get('status', {}).get('code', 'unknown'),
            'status_description_unicobros': data.get('data', {}).get('payment', {}).get('status', {}).get('text', 'Sin descripción'),
        })

        # Acknowledge Unicobros message
        return http.Response('OK', status=200)
