# -*- coding: utf-8 -*-
# Copyright (C) 2024 Axcelere.
# Licensed under the GPL-3.0 License or later.

import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class PosPaywayConfiguration(models.Model):
    _name = 'pos_payway.configuration'
    _description = 'Point of Sale Payway Configuration'

    name = fields.Char(string='Nombre', required=True)
    payway_acquier_id = fields.Char(string="Identificador de comercio", store=True)
    payway_secret_basic = fields.Char(string='Llave secreta')
    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company)