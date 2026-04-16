# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import requests
import logging
_logger = logging.getLogger(__name__)


class MpNotifications(models.Model):
    _name = 'mp.notifications'
    _description = "Pos mp notifications"

    name = fields.Char(string="Referencia Externa")
    credential_id = fields.Many2one('mp.credential', string="Credenciales")
    payment_id = fields.Char(string="Pago Id")
    type = fields.Selection(
        [
            ('point', 'Point'),
            ('qr', 'Qr'),
        ],
        string='Tipo')
    status = fields.Selection(
        [
            ('processed', 'Procesado'),
            ('refunded', 'Devuelto'),
            ('expired', 'Expirado'),
            ('canceled', 'Cancelación'),
            ('failed', 'Falló'),
            ('action_required', 'Acción requerida'),
        ],
        string='Estado')
    request = fields.Text(string="Request")