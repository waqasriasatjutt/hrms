# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class PosConfig(models.Model):
    _inherit = "pos.config"

    auto_lock_enabled = fields.Boolean(string="Enable POS Auto Lock", default=False)
    auto_lock_time = fields.Integer(string="Lock Timeout (seconds)", default=60,
                                    help="Amount of idle time before the screen locks.")

    @api.constrains('auto_lock_time')
    def _check_auto_lock_time(self):
        for config in self:
            if config.auto_lock_enabled and config.auto_lock_time <= 0:
                raise ValidationError(_("The lock timeout must be a positive number."))


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    auto_lock_enabled = fields.Boolean(
        string="Enable POS Auto Lock", related="pos_config_id.auto_lock_enabled", readonly=False)
    auto_lock_time = fields.Integer(string="POS Autolock Time (seconds)", related="pos_config_id.auto_lock_time",
                                    readonly=False, )
    