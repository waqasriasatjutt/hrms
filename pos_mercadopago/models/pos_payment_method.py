# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import models, fields, api, _
_logger = logging.getLogger(__name__)


class PoSPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    pos_mp_config_id = fields.Many2one('mp.credential', string='MP Credentials')
    mp_payment_method_type = fields.Selection([('debit_card', 'Tarjeta débito'), ('credit_card', 'Tarjeta crédito'), ('account_money', 'Dinero en billetare'),('prepaid_card', 'Tarjeta prepago')], string='Modo de pago', default="credit_card")