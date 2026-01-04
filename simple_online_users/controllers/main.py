# -*- coding: utf-8 -*-
# Part of Simple Online Users. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

class OnlineUsersController(http.Controller):

    def _ensure_current_user_presence(self):
        """Ensure current user has up-to-date presence record"""
        try:
            current_user = request.env.user
            current_time = datetime.now()
            
            # Find or create presence record
            presence = request.env['bus.presence'].sudo().search([
                ('user_id', '=', current_user.id)
            ], limit=1)
            
            if presence:
                # Update if older than 1 minute
                time_diff = (current_time - presence.last_poll).total_seconds() / 60 if presence.last_poll else 999
                if time_diff > 1:
                    presence.write({
                        'last_poll': current_time,
                        'last_presence': current_time,
                        'status': 'online'
                    })
            else:
                # Create new presence record
                request.env['bus.presence'].sudo().create({
                    'user_id': current_user.id,
                    'last_poll': current_time,
                    'last_presence': current_time,
                    'status': 'online'
                })
                
        except Exception as e:
            _logger.warning("Could not update presence for current user: %s", e)

    def _get_online_users_data(self):
        """Common method to get online users data with consistent logic"""
        try:
            # Ensure current user's presence is up to date
            self._ensure_current_user_presence()
            
            # Get all active internal users
            active_users = request.env['res.users'].sudo().search([
                ('active', '=', True),
                ('share', '=', False)  # Exclude portal users
            ])
            
            users_data = []
            current_time = datetime.now()
            
            for user in active_users:
                # Get the most recent presence record for this user
                presence = request.env['bus.presence'].sudo().search([
                    ('user_id', '=', user.id)
                ], limit=1, order='last_poll desc')
                
                if presence and presence.last_poll:
                    # Calculate time difference in minutes
                    last_poll_diff = (current_time - presence.last_poll).total_seconds() / 60
                    
                    # Determine actual status based on recent activity
                    if last_poll_diff < 1:  # Less than 1 minute = truly online
                        actual_status = 'online'
                        status_text = 'Active now'
                    elif last_poll_diff < 3:  # 1-3 minutes = away (maybe idle tab)
                        actual_status = 'away'
                        status_text = f'Away ({int(last_poll_diff)}min)'
                    elif last_poll_diff < 5:  # 3-5 minutes = idle (probably stepped away)
                        actual_status = 'idle'
                        status_text = f'Idle ({int(last_poll_diff)}min)'
                    else:
                        # More than 5 minutes = offline (likely closed browser/tab)
                        continue
                    
                    users_data.append({
                        'id': user.id,
                        'name': user.name,
                        'login': user.login,
                        'status': actual_status,
                        'status_text': status_text,
                        'last_poll_minutes': int(last_poll_diff),
                        'avatar_url': f'/web/image/res.users/{user.id}/avatar_128',
                        'is_current_user': user.id == request.env.user.id,
                    })
            return users_data
            
        except Exception as e:
            _logger.error("Error getting online users data: %s", e, exc_info=True)
            return []

    @http.route('/online_users/get_count', type='json', auth='user')
    def get_online_count(self):
        """Get count of currently online users using consistent logic"""
        try:
            # Use the same logic as get_online_users for consistency
            users_data = self._get_online_users_data()
            
            # Count users that are online or away (actively online)
            online_count = len([u for u in users_data if u['status'] in ['online', 'away']])
            
            return {'count': online_count, 'success': True}
        except Exception as e:
            _logger.error("Error getting online users count: %s", e, exc_info=True)
            return {'count': 0, 'success': False, 'error': str(e)}

    @http.route('/online_users/get_visibility_group', type='json', auth='user')
    def get_visibility_group(self):
        """Get the group that can see online users"""
        try:
            param = request.env['ir.config_parameter'].sudo().get_param(
                'online_users.visibility_group', 'base.group_system'
            )
            return {'group_xml_id': param, 'success': True}
        except Exception as e:
            _logger.error("Error getting visibility group: %s", e)
            return {'group_xml_id': 'base.group_system', 'success': False}


    @http.route('/online_users/get_online_users', type='json', auth='user')
    def get_online_users(self):
        """Get list of online users for the popup"""
        try:
            users_data = self._get_online_users_data()
            
            # Sort by status priority and then by last activity
            status_priority = {'online': 0, 'away': 1, 'idle': 2}
            users_data.sort(key=lambda x: (status_priority.get(x['status'], 99), x['last_poll_minutes']))
            
            return {'users': users_data, 'success': True}
        except Exception as e:
            _logger.error("Error getting online users list: %s", e, exc_info=True)
            return {'users': [], 'success': False, 'error': str(e)}