# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################
from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    address_autocomplete = fields.Boolean(string="Address AutoComplete", config_parameter="address_autocomplete")
    google_api_key = fields.Char(string='Google API Key', config_parameter="google_api_key")