from odoo import fields
from odoo.http import request
import json
import logging
import odoo
_logger = logging.getLogger(__name__)

def log_payrillium_event(execution_id, step_name, kind, payload=None, success=True, error_message=None ,env=None):
    # Import masking function
    from ..services.mirillium.utils import _mask_sensitive_data
    
    # Mask sensitive data in payload before logging
    masked_payload = _mask_sensitive_data(payload) if payload else None
    _logger.info("  Logging event: %s | %s | %s | %s", step_name, execution_id, " " if success else " ", masked_payload or error_message)
    try:
        if env:
            odoo_env = env
        elif getattr(request, "env", None):
            odoo_env = request.env



        log_values = {
            'timestamp': fields.Datetime.now(),
            'execution_id': execution_id or 'missing',
            'endpoint': step_name,
            'log_type': kind,
            'success': success,
            'error_message': error_message or "",
        }

        if kind == "request":
            # Mask sensitive data before storing
            masked_for_storage = _mask_sensitive_data(payload) if payload else {}
            log_values['request_payload'] = json.dumps(masked_for_storage)
        else:
            # Mask sensitive data before storing
            masked_for_storage = _mask_sensitive_data(payload) if payload else {}
            log_values['response_payload'] = json.dumps(masked_for_storage)

        record = odoo_env['payrillium.log'].sudo().create(log_values)
  
        _logger.info("  Log saved: ID=%s, type=%s, endpoint=%s", record.id, kind, step_name)
    except Exception as e:
        _logger.error("   Error logging Payrillium event: %s", e)
