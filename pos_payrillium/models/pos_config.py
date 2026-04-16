# -*- coding: utf-8 -*-
from odoo import models, fields


class PosConfig(models.Model):
    _inherit = "pos.config"

    payrillium_terminal_id = fields.Many2one(
        'payrillium.terminal',
        string='Payrillium Terminal',
        ondelete='set null',
        store=True
    )

    payrillium_terminal_name = fields.Char(
        string="Terminal Name",
        related='payrillium_terminal_id.name',
        store=True,
        readonly=True
    )
    payrillium_terminal_serial = fields.Char(
        string="Terminal Serial",
        related='payrillium_terminal_id.serial',
        store=True,
        readonly=True
    )
