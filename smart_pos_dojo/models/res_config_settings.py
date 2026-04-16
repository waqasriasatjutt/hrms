# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _
from odoo.exceptions import UserError
import requests
from datetime import datetime


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    dojo_payment_terminal = fields.Boolean(
        string="Dojo Payment Terminal",
        config_parameter='smart_pos_dojo.dojo_payment_terminal')

    dojo_registration_key = fields.Char(
        string="Smart Dojo Key",
        config_parameter='smart_pos_dojo.registration_key'
    )

    def set_values(self):
        super().set_values()
        payment_methods = self.env['pos.payment.method'].sudo()
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        if not IrConfigParameter.get_param('smart_pos_dojo.dojo_payment_terminal'):
            payment_methods |= payment_methods.search([('use_payment_terminal', '=', 'dojo')])
        if payment_methods:
            payment_methods.write({
                'use_payment_terminal': False,
            })

    def _dojo_deactivate(self, can_resubmit=False):
        # Try automatic resubmission before clearing everything
        if not self.env.context.get('smart_resubmission_in_progress'):
            success = False
            if can_resubmit:
                try:
                    success = self.with_context(smart_resubmission_in_progress=True).generate_smart_dojo_key()
                except Exception:
                    success = False
            if not can_resubmit or not success:
                IrConfigParameter = self.env['ir.config_parameter'].sudo()
                IrConfigParameter.set_param('smart_pos_dojo.registration_key', '')
                IrConfigParameter.set_param('smart_pos_dojo.validation_date', '')
                self.env['pos.payment.method'].sudo().search([
                    ('use_payment_terminal', '=', 'dojo'),
                ]).with_context(dojo_activation='deactivate').write({'active': False})

    def _dojo_activate(self, data):
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        if data and data.get('result') == 'success':
            if 'key' in data:
                IrConfigParameter.set_param('smart_pos_dojo.registration_key', data.get('key') or '')
            IrConfigParameter.set_param('smart_pos_dojo.validation_date', datetime.now().date().strftime('%Y-%m-%d'))

            self.env['pos.payment.method'].sudo().search([
                ('active', '=', False),
                ('use_payment_terminal', '=', 'dojo'),
            ]).with_context(dojo_activation='activate').write({'active': True})

    def _smart_dojo_payload(self):
        base_module = self.env['ir.module.module'].search([['name', '=', 'base']])
        payload = {
            'module': 'smart_pos_dojo',
            'db_uuid': self.env['ir.config_parameter'].sudo().get_param('database.uuid'),
            'base_url': self.env['ir.config_parameter'].sudo().get_param('web.base.url'),
            'version': base_module.latest_version.split('.')[0],
            'company_name': self.env.company.name,
            'customer_email': self.env.company.email,
            'data_lines': [
                {'user': pm.dojo_username}
                for pm in self.env['pos.payment.method'].sudo().with_context(active_test=False).search([])
                if pm.use_payment_terminal == 'dojo'
            ]
        }
        if self.env.context.get('smart_resubmission_in_progress'):
            payload['is_automatic_resubmission'] = True
        return payload

    def _smart_dojo_post(self, url=False, endpoint=False, headers=False, json=False, raise_exc=True):
        data = {}
        try:
            full_url = url.strip('/ ') + '/' + endpoint.strip('/ ')
            response = requests.post(full_url, headers=headers, json=json, timeout=10)

            # Validate Response
            if response.status_code != 200:
                raise UserError(_("Failed to generate key: Error code " + str(response.status_code)))

            try:
                data = response.json()
            except ValueError:
                pass

            if not data or not data.get('result'):
                raise UserError(_("Empty response from server"))
        except Exception:
            if raise_exc:
                raise

        return data

    def generate_smart_dojo_key(self):
        # Build request
        payload = self._smart_dojo_payload()
        # Send request
        data = self._smart_dojo_post(
            url='https://smart-ltd.co.uk',
            endpoint='/smart/key/generate',
            headers={'Content-Type': 'application/json'},
            json=payload
        )

        # Process Response
        if data['result'] == 'success':
            self._dojo_activate(data)
            return True
        else:
            raise UserError(_("Registration Failed: %s") % data.get('reason'))
        return False

    def _validate_smart_dojo_key(self):
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        key = IrConfigParameter.get_param('smart_pos_dojo.registration_key')
        if not key:
            self._dojo_deactivate(can_resubmit=True)
            return

        # Build request
        payload = self._smart_dojo_payload()
        payload['key'] = key
        # Send request
        data = self._smart_dojo_post(
            url='https://smart-ltd.co.uk',
            endpoint='/smart/key/validate',
            headers={'Content-Type': 'application/json'},
            json=payload,
            raise_exc=False
        )

        # Process Response
        if data and data.get('result') == 'success':
            self._dojo_activate(data)
        elif data and data.get('result') == 'fail':
            self._dojo_deactivate(can_resubmit=True)
        elif not data or data.get('result', 'error') == 'error':
            # deactivate if no date set or X days passed since last validation
            try:
                last_date_str = IrConfigParameter.get_param('smart_pos_dojo.validation_date')
                last_date = datetime.strptime(last_date_str, '%Y-%m-%d')
            except (ValueError, TypeError):
                last_date = False
            if not last_date or (datetime.now().date() - last_date.date()).days >= 5:
                self._dojo_deactivate(can_resubmit=False)
