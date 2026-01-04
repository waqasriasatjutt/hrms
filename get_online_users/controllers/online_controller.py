from odoo import http
from odoo.http import request
from datetime import datetime, timedelta

UPDATE_PRESENCE_DELAY = 60      # seconds
AWAY_TIMER = 1800               # seconds (30 minutes)

class UserPresenceAPI(http.Controller):

    def _authenticate_token(self, token):
        allowed_token = request.env['ir.config_parameter'].sudo().get_param('custom_api.token')
        return token == allowed_token

    @http.route('/api/public/online_u', type='json', auth='public', csrf=False)
    def public_online_u(self):
        now = datetime.now()

        active_users = request.env['res.users'].sudo().search([
            ('active', '=', True),
            ('share', '=', False)  # Exclude portal users
        ])
        
        users_data = []
        current_time = datetime.now()
        
        for user in active_users:
            # Get the most recent presence record for this user
            online_users = request.env['bus.presence'].sudo().search([
                ('user_id', '=', user.id)
            ], limit=1, order='last_poll desc')


            result = []
            result.append({
                        'name': "waqas",
                        'email': "waqas@gmail.com",
                        'login': "user.login",
                        'online_since': "",
                        'status': "online",
                        'users': online_users,
                        'user': user
                    })

            for presence in online_users:
                user = presence.user_id
                if not user or not presence.last_poll:
                    continue

                # Calculate time delta
                delta = (now - presence.last_poll).total_seconds()

                # Dynamically compute status
                if delta <= UPDATE_PRESENCE_DELAY:
                    status = 'online'
                elif delta <= AWAY_TIMER:
                    status = 'away'
                else:
                    status = 'offline'
                result.append({
                        'name': user.name,
                        'email': user.email,
                        'login': user.login,
                        'online_since': presence.last_poll,
                        'status': status,
                    })

        return result
