# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class MPStoreBoxLine(models.Model):
    _inherit = 'mp.store.box.line'

    image_qr = fields.Char(string="Image QR")
    template_document_qr = fields.Char(string="Template document QR")
    template_image_qr = fields.Char(string="Template image QR")
    qr_code = fields.Char(string="QR code")

    def action_get_qr(self):
        url = self.image_qr
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    def action_get_qr_label(self):
        url = self.template_document_qr
        if not url:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Aviso',
                    'message': 'El punto de venta no tiene asociado un QR.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }
