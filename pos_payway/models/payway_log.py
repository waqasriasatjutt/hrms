# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import models, fields, api, _
_logger = logging.getLogger(__name__)


class PaywayLog(models.Model):
    _name = 'payway.log'
    _description = 'Payway Log'
    _rec_name = 'session_id'

    session_id = fields.Many2one('pos.session', string="Sesión")
    action = fields.Selection(
        [
            ('create_order', 'Crear orden'),
            ('remove_order', 'Eliminar orden'),
            ('get_order', 'Obtener orden'),
            ('refund_order', 'Devolver orden'),
            ('box_closed', 'Cierre de Caja'),
        ],
        string='Action'
    )
    header = fields.Char(string="Header")
    endpoint = fields.Char(string="Endpoint")
    status_code = fields.Char(string="Status code")
    request = fields.Text(string="Request")
    response = fields.Text(string="Response")
    payment_id = fields.Char(string="Identificador del pago")

    def create_logs(self, session_id, action, headers, endpoint, status_code, payload, response):
        log_id = self.env['payway.log'].create({
            'session_id': session_id.id,
            'action': action,
            'header': headers,
            'endpoint': endpoint,
            'status_code': status_code,
            'request': payload,
            'response': response,
        })
        return log_id

