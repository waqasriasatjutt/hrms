# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import requests
from odoo import fields, exceptions, models, _, api
from odoo.exceptions import UserError
from requests.auth import HTTPBasicAuth


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    dojo_acct_name = fields.Char('Account Name')
    dojo_url = fields.Char('API URL')
    dojo_username = fields.Char('Username')
    dojo_key = fields.Char('API Key')
    installer_id = fields.Char('Installer-ID')
    terminal_id = fields.Char('Terminal-ID')

    # def dojo_make_payment_request(self, data):
    #     import time
    #
    #     time.sleep(2)
    #     headers = {
    #         'Content-Type': 'application/json',
    #         'Accept': 'application/connect.v2+json',
    #         'Software-House-Id': self.env.company.software_house_id,
    #         'Installer-Id': self.installer_id,
    #     }
    #     url = self.dojo_url + '/pac/terminals/' + self.terminal_id + '/transactions'
    #
    #     response = requests.post(
    #         url,
    #         headers = headers,
    #         data=json.dumps(data),
    #         auth=HTTPBasicAuth(self.dojo_username, self.dojo_key)
    #     )
    #     return response.json()

    @api.model
    def _load_pos_data_fields(self, config_id):
        result = super()._load_pos_data_fields(config_id)
        result += ['dojo_acct_name', 'dojo_url', 'dojo_username', 'dojo_key', 'installer_id', 'terminal_id']
        return result

    def _get_payment_terminal_selection(self):
        selection_list = super(PosPaymentMethod, self)._get_payment_terminal_selection()
        if self.env['ir.config_parameter'].sudo().get_param('smart_pos_dojo.dojo_payment_terminal'):
            selection_list.append(('dojo', 'Dojo'))
        return selection_list

    def _is_write_forbidden(self, fields):
        # Allow active state to be changed while a pos session is still open
        return super(PosPaymentMethod, self)._is_write_forbidden(fields - {'active'})

    def write(self, vals):
        res = super(PosPaymentMethod, self).write(vals)

        # If activating / changing to Dojo and the check doesn't pass, archive the dojo methods
        if vals.get('active') or vals.get('use_payment_terminal') == 'dojo':
            IrConfigParameter = self.env['ir.config_parameter'].sudo()
            if not IrConfigParameter.get_param('smart_pos_dojo.registration_key'):
                dojo_self = self.filtered(lambda x: x.use_payment_terminal == 'dojo')
                super(PosPaymentMethod, dojo_self).write({'active': False})

        for record in self:
            if record.use_payment_terminal == 'dojo' and not self.env.context.get('dojo_activation'):
                fields = ['dojo_acct_name', 'dojo_username', 'dojo_url', 'dojo_key', 'installer_id']
                for key in fields:
                    if not getattr(record, key):
                        field_name = record._fields[key].string
                        raise UserError(_('Please configure required Fields : %s' % field_name))
                if not record.company_id.software_house_id:
                    raise UserError(_('Please configure Software House ID in Company Configuration.'))
                try:
                    response = requests.get(
                        '{}/pac/terminals?status=AVAILABLE&currency=GBP'.format(record.dojo_url),
                        headers={
                            'Content-Type': 'application/json',
                            'Accept': 'application/connect.v2+json',
                            'Software-House-Id': record.company_id.software_house_id,
                            'Installer-Id': record.installer_id,
                        },
                        auth=HTTPBasicAuth(record.dojo_username, record.dojo_key),
                        timeout=10
                    )
                    if response.status_code < 200 or response.status_code >= 300:
                        raise UserError(_("ERROR " + str(response.status_code) + ": " + response.text))
                except requests.exceptions.RequestException as e:
                    raise exceptions.UserError(e)

        return res

    def get_terminal_id(self):
        fields = ['dojo_acct_name', 'dojo_username', 'dojo_url', 'dojo_key', 'installer_id']
        for key in fields:
            if not getattr(self, key):
                field_name = self._fields[key].string
                raise UserError(_('Please configure required Fields : %s'% field_name))
        if not self.company_id.software_house_id:
            raise UserError(_('Please Configure Software House Id in Company Configuration.'))
        url_key = '{}/pac/terminals?status=AVAILABLE&currency=GBP'.format(self.dojo_url)
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/connect.v2+json',
            'Software-House-Id': self.company_id.software_house_id,
            'Installer-Id': self.installer_id,
        }
        response = requests.get(
            url_key,
            headers=headers,
            auth=HTTPBasicAuth(self.dojo_username, self.dojo_key)
        )
        if response.status_code < 200 or response.status_code >= 300:
            raise UserError(_("ERROR " + str(response.status_code) + ": " + response.text))
        data = response.json()
        self.sudo().write({
            'terminal_id': [terminal['tid'] for terminal in data['terminals']]
        })
        return True
