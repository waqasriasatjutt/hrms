import logging

from odoo import api, models, _

_logger = logging.getLogger(__name__)


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    def _get_available_qr_methods(self):
        rslt = super()._get_available_qr_methods()
        rslt.append(('qr30', _("QR Tag 30"), 50))
        return rslt
