# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import json

class RewardsCodesConfig(models.Model):
    _name = 'rewardscodes.config'
    _description = _('Rewards Codes Config')

    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True
    )

    demo = fields.Boolean(
        string=_('Demo Mode'),
        default=True,
        help=_('If enabled, Rewards Codes runs with demo credentials and sample data.')
    )

    phone = fields.Char(
        string=_('Owner Phone'),
        help=_('Phone number used to create your account at https://partner.rewards.codes. '
               'Must include the country code, e.g. +52XXXXXXXXXX.')
    )

    default_phone_code = fields.Char(
        string=_("Default Phone Code"),
        help=_('The country code used for customer numbers. Example: +52 or +1.')
    )

    api_key = fields.Char(
        string=_('API Key'),
        help=_('Your developer key located at the bottom of the Settings page in https://partner.rewards.codes.')
    )

    qr = fields.Boolean(
        string=_('QR on Ticket'),
        default=False,
        help=_('Enable this option to print a Rewards Codes QR on customer receipts or tickets.')
    )

    mode = fields.Selection(
        [
            ('visit',  _('Visits Mode')),
            ('product', _('Products Mode')),
            ('emoney', _('E-Money Mode')),
        ],
        string=_('Mode'),
        required=True,
        default='visit',
        help=_('Select the type of rewards: Visits, Products, or E-Money.')
    )

    # Porcentaje de dinero electrónico a regresar (ej. 1.0 = 1%)
    emoney_percent = fields.Float(
        string=_('E-Money Percentage'),
        default=1.0,
        help=_('Percentage of the order total returned to the customer as electronic money. '
               'Example: 1.0 = 1%%.')
    )

    _sql_constraints = [
        ('rwc_singleton_company',
         'unique(company_id)',
         _('Only one Rewards Codes configuration is allowed per company.'))
    ]

    # ---------------------------------------------------------------------
    #  VALIDATION: Prevent disabling demo until fields are complete
    # ---------------------------------------------------------------------
    @api.constrains('demo', 'phone', 'api_key', 'default_phone_code')
    def _check_demo_requirements(self):
        for rec in self:
            if not rec.demo:
                missing = []
                if not rec.phone:
                    missing.append(_("Phone"))
                if not rec.api_key:
                    missing.append(_("API Key"))
                if not rec.default_phone_code:
                    missing.append(_("Default Phone Code"))
                if missing:
                    raise ValidationError(
                        _("To disable Demo Mode, please fill the following fields: %s") %
                        ", ".join(missing)
                    )

    # ---------------------------------------------------------------------
    #  ONCHANGE: auto-fill defaults when demo mode is activated
    # ---------------------------------------------------------------------
    @api.onchange('demo')
    def _onchange_demo(self):
        """Fill demo data when demo=True."""
        if self.demo:
            self.phone = '+524921073690'
            self.default_phone_code = '+52'
            self.api_key = '74e697e4bff5bf1dd2d9f45966fdfb861e9f02b88abf40a9c4d86229f9b0a74f'
            self.qr = True
            self.mode = 'visit'
            self.emoney_percent = 1.0  # 1% por defecto en demo

    # ---------------------------------------------------------------------
    #  AUTO-FILL defaults on creation if demo=True
    # ---------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            company_id = vals.get('company_id') or self.env.company.id
            exists = self.search_count([('company_id', '=', company_id)])
            if exists:
                raise ValidationError(_('Only one Rewards Codes configuration is allowed per company.'))

            if vals.get('demo', True):
                vals.setdefault('phone', '+524921073690')
                vals.setdefault('default_phone_code', '+52')
                vals.setdefault('api_key', '74e697e4bff5bf1dd2d9f45966fdfb861e9f02b88abf40a9c4d86229f9b0a74f')
                vals.setdefault('qr', True)
                vals.setdefault('mode', 'visit')
                vals.setdefault('emoney_percent', 1.0)

        return super().create(vals_list)

    # ---------------------------------------------------------------------
    #  HELPER: Get config for current company (used by POS / API)
    # ---------------------------------------------------------------------
    @api.model
    def get_all(self):
        conf = self.search([('company_id', '=', self.env.company.id)], limit=1)
        if not conf:
            return json.dumps({})

        if conf.demo:
            data = {
                'demo': True,
                'phone': '+524921073690',
                'default_phone_code': '+52',
                'api_key': '74e697e4bff5bf1dd2d9f45966fdfb861e9f02b88abf40a9c4d86229f9b0a74f',
                'qr': True,
                'mode': 'visit',
                'emoney_percent': 1.0,
                'demo_data': {
                    'info': _('Demo Mode active — using simulated credentials.'),
                    'company': self.env.company.name,
                },
            }
        else:
            data = {
                'demo': False,
                'phone': conf.phone or '',
                'default_phone_code': conf.default_phone_code or '',
                'api_key': conf.api_key or '',
                'qr': bool(conf.qr),
                'mode': conf.mode or 'visit',
                'emoney_percent': conf.emoney_percent or 0.0,
            }

        return json.dumps(data)

    # ---------------------------------------------------------------------
    #  INIT: create default config per company on module install/update
    # ---------------------------------------------------------------------
    @api.model
    def init(self):
        """Ensure each company has exactly one Rewards Codes config.

        Called when the module is installed or updated (registry init).
        """
        Config = self.env['rewardscodes.config'].sudo()
        companies = self.env['res.company'].sudo().search([])
        for company in companies:
            exists = Config.search_count([('company_id', '=', company.id)])
            if not exists:
                Config.create({
                    'company_id': company.id,
                    # demo=True by default; create() will fill the demo fields.
                })
