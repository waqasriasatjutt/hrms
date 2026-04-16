import logging

from odoo import fields, models, _
from odoo.exceptions import AccessError

from .unicobros_pos_request import UnicobrosPosRequest

_logger = logging.getLogger(__name__)


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    uni_bearer_token = fields.Char(
        string="Access Token de la entidad",
        groups="point_of_sale.group_pos_manager")
    uni_api_key_entity = fields.Char(
        string="API Key de la entidad",
        groups="point_of_sale.group_pos_manager")
    uni_id_point_smart = fields.Char(
        string="POS DEVICE ID")
    
    
    def _get_payment_terminal_selection(self):
        return super()._get_payment_terminal_selection() + [('unicobros', 'Unicobros')]

    def _check_special_access(self):
        if not self.env.user.has_group('point_of_sale.group_pos_user'):
            raise AccessError(_("Do not have access to fetch token from Unicobros"))

    def uni_payment_intent_create(self, infos):
        """
        Called from frontend for creating a payment intent in Unicobros
        """
        self._check_special_access()

        unicobros = UnicobrosPosRequest(self.sudo().uni_bearer_token, self.sudo().uni_api_key_entity)
        # Call Unicobros for payment intend creation
        resp = unicobros.call_unicobros("post", f"{self.uni_id_point_smart}/operation", infos)
        _logger.debug("uni_payment_intent_create(), response from Unicobros: %s", resp)
        return resp

    def uni_payment_intent_cancel(self):
        """
        Called from frontend to cancel a payment intent in Unicobros
        """
        self._check_special_access()

        unicobros = UnicobrosPosRequest(self.sudo().uni_bearer_token, self.sudo().uni_api_key_entity)
        # Call Unicobros for payment intend cancelation
        resp = unicobros.call_unicobros("delete", f"/{self.uni_id_point_smart}/operation", {})
        
        return resp
