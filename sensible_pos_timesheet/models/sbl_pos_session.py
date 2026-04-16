# Powered by Sensible Consulting Services
# -*- coding: utf-8 -*-
# © 2025 Sensible Consulting Services (<https://sensiblecs.com/>)

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ScPosSession(models.Model):
    _inherit = 'pos.session'

    sbl_attendance_ids = fields.One2many(
        'hr.attendance',
        'sbl_pos_session_id',
        string='Attendance Records',
        help='Timesheet records for this POS session'
    )
    sbl_attendance_count = fields.Integer(
        string='Attendance Count',
        compute='_compute_attendance_count'
    )
    sbl_current_attendance_id = fields.Many2one(
        'hr.attendance',
        string='Current Attendance',
        help='Current active attendance record for this session'
    )

    @api.depends('sbl_attendance_ids')
    def _compute_attendance_count(self):
        for session in self:
            session.sbl_attendance_count = len(session.sbl_attendance_ids)

    @api.model
    def sbl_create_attendance_checkin(self, session_id):
        """Create attendance check-in for POS session using Odoo's standard method"""
        try:
            session = self.search([('id', '=', session_id)], limit=1)
            
            if not session:
                return {'status': 'error', 'message': f'POS session {session_id} not found'}

            # Check if user exists and has proper access
            try:
                user = session.user_id
                if not user.exists():
                    return {'status': 'error', 'message': 'Session user not found'}
                    
                # Use sudo to check employee existence, but validate access properly
                employee = user.employee_id
                if not employee:
                    return {'status': 'error', 'message': f'No employee found for user {user.name}. Please create an employee record for this user.'}
                
                # Check if employee record exists with proper access rights
                if not employee.exists():
                    return {'status': 'error', 'message': f'Employee record does not exist for user {user.name}'}
                    
            except Exception as access_error:
                _logger.error(f"Employee access error for session {session_id}: {str(access_error)}")
                return {'status': 'error', 'message': f'Unable to access employee record. Please check user permissions or contact administrator.'}

            # Use Odoo's standard attendance method (handles check-in logic)
            attendance = employee.sudo()._attendance_action_change()

            # Link attendance to POS session
            if attendance:
                attendance.sudo().write({'sbl_pos_session_id': session.id})
                _logger.info(f"POS Session {session.name} - Check-in created for employee {employee.name}")
                return {'status': 'success', 'attendance_id': attendance.id}
            else:
                return {'status': 'error', 'message': 'Failed to create attendance check-in'}

        except Exception as e:
            _logger.error(f"Check-in error for session {session_id}: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    @api.model
    def sbl_create_attendance_checkout(self, session_id):
        """Create attendance check-out for POS session using Odoo's standard method"""
        try:
            session = self.search([('id', '=', session_id)], limit=1)
            
            if not session:
                return {'status': 'error', 'message': f'POS session {session_id} not found'}

            # Check if user exists and has proper access
            try:
                user = session.user_id
                if not user.exists():
                    return {'status': 'error', 'message': 'Session user not found'}
                    
                # Use sudo to check employee existence, but validate access properly
                employee = user.employee_id
                if not employee:
                    return {'status': 'error', 'message': f'No employee found for user {user.name}. Please create an employee record for this user.'}
                
                # Check if employee record exists with proper access rights
                if not employee.exists():
                    return {'status': 'error', 'message': f'Employee record does not exist for user {user.name}'}
                    
            except Exception as access_error:
                _logger.error(f"Employee access error for session {session_id}: {str(access_error)}")
                return {'status': 'error', 'message': f'Unable to access employee record. Please check user permissions or contact administrator.'}

            # Use Odoo's standard attendance method (handles check-out logic)
            attendance = employee.sudo()._attendance_action_change()

            _logger.info(f"POS Session {session.name} - Check-out completed for employee {employee.name}")
            return {'status': 'success', 'attendance_id': attendance.id if attendance else None}

        except Exception as e:
            _logger.error(f"Check-out error for session {session_id}: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    def action_view_attendance_records(self):
        self.ensure_one()
        action = self.env.ref("hr_attendance.hr_attendance_action").read()[0]
        action.update({
            'domain': [('id', 'in', self.sbl_attendance_ids.ids)],
            'context': {
                'default_sbl_pos_session_id': self.id,
                'default_employee_id': self.user_id.employee_id.id if self.user_id.employee_id else False,
            }
        })
        return action
