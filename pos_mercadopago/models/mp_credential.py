# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import requests
import uuid
from datetime import timedelta
from urllib.parse import urlencode
from odoo import models, fields, api, _
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class MPCredential(models.Model):
    _name = 'mp.credential'
    _description = 'Point of Sale MP Configuration'

    name = fields.Char(string='Name', required=True)
    mp_url = fields.Char(string='Url', required=True, default="https://api.mercadopago.com")
    user_id = fields.Char(string='Usuario')
    mp_access_token = fields.Char(string='Access token')
    payment_type = fields.Selection([], string='Tipo')
    platform_id = fields.Char(string='Plataforma ID', default="dev_f4f46d98628911ec998f0242ac130004")
    integrator_id = fields.Char(string='Integrador ID', default="dev_f4f46d98628911ec998f0242ac130004")
    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company)
    
    # OAuth fields
    client_id = fields.Char(string='Client ID', required=True)
    client_secret = fields.Char(string='Client Secret', required=True)
    mp_webhook_secret = fields.Char(
        string="Secret Key Webhook",
        groups="point_of_sale.group_pos_manager")
    refresh_token = fields.Char(string='Refresh Token')
    redirect_uri = fields.Char(string='Redirect URI', required=True, default=lambda self: self._default_redirect_uri())
    authorization_code = fields.Char(string='Authorization Code', help='Code received from authorization callback')
    state = fields.Char(string='OAuth State', help='Random state for security')
    
    # Token response fields
    token_type = fields.Char(string='Token Type')
    expires_in = fields.Integer(string='Expiración en (segundos)')
    user_id = fields.Char(string='Usuario ID')
    scope = fields.Char(string='Scope', readonly=True)
    public_key = fields.Char(string='Llave publica')
    live_mode = fields.Boolean(string='Live Mode')
    token_obtained_date = fields.Datetime(string='Fecha de obtención del token')
    token_expiry_date = fields.Datetime(string='Fecha de expiración del token', compute='_compute_token_expiry_date', store=True)

    @api.depends('token_obtained_date', 'expires_in')
    def _compute_token_expiry_date(self):
        for record in self:
            if record.token_obtained_date and record.expires_in:
                record.token_expiry_date = record.token_obtained_date + timedelta(seconds=record.expires_in)
            else:
                record.token_expiry_date = False

    def _default_redirect_uri(self):
        """
        Get default redirect URI using current Odoo base URL
        """
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if base_url:
            return f"{base_url}/mercadopago/oauth/callback"
        return "https://yourdomain.com/mercadopago/oauth/callback"

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override create to set default redirect_uri based on current Odoo domain
        """
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        default_redirect_uri = f"{base_url}/mercadopago/oauth/callback" if base_url else "https://yourdomain.com/mercadopago/oauth/callback"
        
        for vals in vals_list:
            if not vals.get('redirect_uri'):
                vals['redirect_uri'] = default_redirect_uri
        
        return super().create(vals_list)

    def generate_authorization_url(self):
        """
        Generate MercadoPago authorization URL for OAuth flow
        Format: https://auth.mercadopago.com/authorization?client_id=APP_ID&response_type=code&platform_id=mp&state=RANDOM_ID&redirect_uri=URL
        """
        if not self.client_id or not self.redirect_uri:
            raise UserError(_('Client ID and Redirect URI are required'))

        # Generate random state for security (unique identifier, no sensitive info)
        state = str(uuid.uuid4()).replace('-', '')
        self.state = state

        # Use the standard MercadoPago authorization URL
        base_url = 'https://auth.mercadopago.com/authorization'

        params = {
            'client_id': self.client_id,           # APP_ID from application details
            'response_type': 'code',               # Required for authorization_code flow
            'platform_id': 'mp',                   # MercadoPago platform identifier
            'state': state,                        # RANDOM_ID unique for each attempt
            'redirect_uri': self.redirect_uri      # URL from "URLs de redireccionamiento" in app
        }

        authorization_url = f"{base_url}?{urlencode(params)}"
        
        _logger.info(f"Generated authorization URL for credential {self.name}: {authorization_url}")
        
        return {
            'type': 'ir.actions.act_url',
            'url': authorization_url,
            'target': 'new'
        }

    def exchange_authorization_code(self):
        """
        Exchange authorization code for access token and refresh token
        1. Make request to MercadoPago API
        2. Send token response to local endpoint for storage
        """
        if not self.client_id or not self.client_secret:
            raise UserError(_('Client ID and Client Secret are required'))
        
        if not self.authorization_code:
            raise UserError(_('Authorization Code is required. Please complete the authorization flow first.'))
        
        if not self.redirect_uri:
            raise UserError(_('Redirect URI is required'))

        # Step 1: Make request to MercadoPago API
        mp_url = f"{self.mp_url}/oauth/token"
        
        payload = {
            'client_secret': self.client_secret,
            'client_id': self.client_id,
            'grant_type': 'authorization_code',
            'code': self.authorization_code,
            'redirect_uri': self.redirect_uri
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            # Request to MercadoPago
            response = requests.post(mp_url, data=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            token_data = response.json()
            _logger.info(f"MercadoPago token response: {token_data}")
            
            # Update credential directly with token data
            self.write({
                'mp_access_token': token_data.get('access_token'),
                'token_type': token_data.get('token_type'),
                'expires_in': token_data.get('expires_in'),
                'scope': token_data.get('scope'),
                'user_id': str(token_data.get('user_id')) if token_data.get('user_id') else False,
                'refresh_token': token_data.get('refresh_token'),
                'public_key': token_data.get('public_key'),
                'live_mode': token_data.get('live_mode', False),
                'token_obtained_date': fields.Datetime.now(),
                'authorization_code': False,  # Clear after successful exchange
            })
            
            _logger.info(f"Token data updated for credential: {self.name}")
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Authorization code exchanged successfully. Refresh token obtained.'),
                    'type': 'success',
                }
            }
            
        except requests.exceptions.RequestException as e:
            error_msg = f"HTTP Error: {str(e)}"
            _logger.error(f"Error exchanging authorization code for credential {self.name}: {error_msg}")
            raise UserError(_(f"Error during token exchange: {error_msg}"))
            
        except (ValueError, KeyError) as e:
            error_msg = f"Invalid response format: {str(e)}"
            _logger.error(f"Error parsing response for credential {self.name}: {error_msg}")
            raise UserError(_(f"Invalid response format: {error_msg}"))

    def _should_refresh_token(self):
        """
        Check if token should be refreshed (5 days before expiry)
        """
        if not self.token_expiry_date or not self.refresh_token:
            return False
        
        # Refresh token 5 days before expiry
        refresh_threshold = self.token_expiry_date - timedelta(days=5)
        return fields.Datetime.now() >= refresh_threshold

    @api.model
    def _cron_refresh_tokens(self):
        """
        Cron job to refresh tokens that are about to expire
        """
        credentials = self.search([
            ('refresh_token', '!=', False),
            ('mp_access_token', '!=', False),
            ('token_expiry_date', '!=', False),
        ])
        
        refreshed_count = 0
        for credential in credentials:
            if credential._should_refresh_token():
                try:
                    credential.refresh_oauth_token()
                    refreshed_count += 1
                    _logger.info(f"Token refreshed automatically for credential: {credential.name}")
                except Exception as e:
                    _logger.error(f"Failed to refresh token for credential {credential.name}: {str(e)}")
        
        _logger.info(f"Cron job completed. {refreshed_count} tokens refreshed out of {len(credentials)} credentials checked.")

    def refresh_oauth_token(self):
        """
        Refresh OAuth token using refresh_token
        """
        if not self.client_id or not self.client_secret:
            raise UserError(_('Client ID and Client Secret are required'))
            
        if not self.refresh_token:
            raise UserError(_('Refresh Token is required to refresh access token'))

        url = f"{self.mp_url}/oauth/token"
        
        payload = {
            'client_secret': self.client_secret,
            'client_id': self.client_id,
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
        }

        headers = {
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Update fields with response data
            self.write({
                'mp_access_token': data.get('access_token'),
                'token_type': data.get('token_type'),
                'expires_in': data.get('expires_in'),
                'scope': data.get('scope'),
                'user_id': str(data.get('user_id')) if data.get('user_id') else self.user_id,
                'refresh_token': data.get('refresh_token') or self.refresh_token,
                'live_mode': data.get('live_mode', self.live_mode),
                'token_obtained_date': fields.Datetime.now(),
            })
            
            _logger.info(f"OAuth token refreshed successfully for credential: {self.name}")
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Token refrescado satisfactoriamente'),
                    'type': 'success',
                }
            }
            
        except requests.exceptions.RequestException as e:
            error_msg = f"HTTP Error: {str(e)}"
            _logger.error(f"Error refreshing OAuth token for credential {self.name}: {error_msg}")
            raise UserError(_(f"Error connecting to MercadoPago API: {error_msg}"))
            
        except (ValueError, KeyError) as e:
            error_msg = f"Invalid response format: {str(e)}"
            _logger.error(f"Error parsing response for credential {self.name}: {error_msg}")
            raise UserError(_(f"Invalid response from MercadoPago API: {error_msg}"))