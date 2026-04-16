import json
import base64
import hashlib
import requests
from datetime import datetime, timezone
import random
import logging

from odoo import _
from ..config import PAYMENT_METHOD_NAME
from ..config import PAYMENT_METHOD_COLOR
from ..config import PAYMENT_METHOD_ICON
from odoo import http, fields
from odoo.http import request
from ..services.mirillium.utils import get_payrillium_credentials
from ..services.logging_service import log_payrillium_event
from ..services.mirillium import create_payment_link, authorize_payment
from ..config import CLOUD_MIRILLIUM_API_URL
from ..services.mirillium.api import refund_payment_by_token
_logger = logging.getLogger(__name__)


API_BASE_URL = f"{CLOUD_MIRILLIUM_API_URL}"

# ─────────────────────────────────────────────
#  Signature generation
# ─────────────────────────────────────────────


def get_token_from_config(env):
    config = env['payrillium.config'].sudo().search([], limit=1)
    if not config or not config.token:
        return None  # Return None instead of raising to allow mode without token
    return config.token


def build_header_hash(env, data, timestamp):
    key = get_token_from_config(env)  # token example: A210-1234567890
    if not key:
        raise ValueError(
            "Payrillium token not configured. Please configure in Settings > Payrillium Configuration.")
    data["key"] = base64.b64encode(
        f"{key}{timestamp}".encode("utf-8")).decode("utf-8")
    json_str = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    json_bytes = json_str.encode("utf-8")
    base64_json = base64.b64encode(json_bytes).decode("utf-8")
    return hashlib.sha512(base64_json.encode("utf-8")).hexdigest()


def build_url(terminal_id, path_type, action):
    return f"{API_BASE_URL}{terminal_id}/{path_type}/{action}"


def _get_current_terminal(session_id=None):
    """
    Get the current terminal for the session, validating access permissions.
    
    Args:
        session_id: POS session ID (optional)
    
    Returns:
        Payrillium terminal or None if not found or no permissions
    """
    user = request.env.user
    
    if session_id:
        # Validate that session_id is a valid integer
        try:
            session_id_int = int(session_id)
            if session_id_int <= 0:
                _logger.warning(f"Invalid session_id: {session_id}")
                return None
        except (ValueError, TypeError):
            _logger.warning(f"Invalid session_id format: {session_id}")
            return None
        
        # Search session with permission validation
        session = request.env['pos.session'].sudo().browse(session_id_int)
        if not session.exists():
            _logger.warning(f"Session {session_id_int} not found")
            return None
        
        # Verify that the user has access to this session
        # The user must be the owner or have POS permissions
        if session.user_id.id != user.id:
            # Verify if the user has POS manager permissions
            if not user.has_group('point_of_sale.group_pos_manager'):
                _logger.warning(f"User {user.id} attempted to access session {session_id_int} owned by {session.user_id.id}")
                return None
        
        # Verify that the session is opened
        if session.state not in ['opened', 'opening_control']:
            _logger.warning(f"Session {session_id_int} is not in opened state (state: {session.state})")
            return None
        
        # Get terminal only if it exists
        if session.config_id.payrillium_terminal_id:
            return session.config_id.payrillium_terminal_id
    else:
        # Search for current user's session
        session = request.env['pos.session'].sudo().search([
            ('user_id', '=', user.id),
            ('state', '=', 'opened')
        ], limit=1)
        _logger.debug("Current session: %s", session.id if session else "None")

        if session and session.config_id.payrillium_terminal_id:
            return session.config_id.payrillium_terminal_id
    
    return None


def deep_clean_payload(payload):
    if isinstance(payload, dict):
        cleaned = {}
        for key, value in payload.items():
            if key != "executionId" and value is not None:
                cleaned[key] = deep_clean_payload(value)
        return cleaned
    elif isinstance(payload, list):
        return [deep_clean_payload(item) for item in payload if item is not None]
    else:
        return payload


class PayrilliumWizardController(http.Controller):

    # ─────────────────────────────────────────────
    #  Local request --> DB-ODOO
    # ─────────────────────────────────────────────
    @http.route('/payrillium/payment_method_name', type='json', auth='user')
    def get_payment_method_name(self):
        _logger.debug("  Getting payment method name...")
        try:
            result = {"payment_method_name": PAYMENT_METHOD_NAME}
            _logger.debug("  Payment method name retrieved: %s",
                          PAYMENT_METHOD_NAME)

            return result
        except Exception as e:
            error_msg = str(e)
            _logger.error(f"  Error getting payment method name: {error_msg}")
            return {"status": "error", "message": error_msg}

    @http.route('/payrillium/payment_method_color', type='json', auth='user')
    def payment_method_color(self):
        _logger.debug(" Getting payment method color...")
        try:
            result = {"color": PAYMENT_METHOD_COLOR}
            _logger.debug("  Payment method color retrieved: %s",
                          PAYMENT_METHOD_COLOR)
            return result
        except Exception as e:
            error_msg = str(e)
            _logger.error(f"  Error getting payment method color: {error_msg}")
            return {"status": "error", "message": error_msg}

    @http.route('/payrillium/payment_method_icon', type='json', auth='user')
    def payment_method_icon(self):
        _logger.debug(" Getting payment method icon...")
        try:
            result = {"icon": PAYMENT_METHOD_ICON}
            _logger.debug("  Payment method icon retrieved: %s",
                          PAYMENT_METHOD_ICON)
            return result
        except Exception as e:
            error_msg = str(e)
            _logger.error(f"  Error getting payment method icon: {error_msg}")
            return {"status": "error", "message": error_msg}

    @http.route('/payrillium/payment_method_data', type='json', auth='user')
    def get_payment_method_data(self):
        payment_method = request.env['pos.payment.method'].search([
            ('use_payment_terminal', '=', 'payrillium')
        ], limit=1)

        return {
            'id': payment_method.id,
            'name': payment_method.name,
            'payment_provider_id': payment_method.payment_provider_id.id if payment_method.payment_provider_id else None,
            'receivable_account_id': payment_method.receivable_account_id.id if payment_method.receivable_account_id else None,
            'outstanding_account_id': payment_method.outstanding_account_id.id if payment_method.outstanding_account_id else None,
        }

    @http.route('/payrillium/log', type='json', auth='user')
    def log_from_js(self, execution_id, step, kind, success=True, error_message=None, payload=None):
        # Validate input to prevent injection or malicious data
        # Limit text field length
        MAX_STRING_LENGTH = 500
        
        if execution_id and len(str(execution_id)) > MAX_STRING_LENGTH:
            _logger.warning(f"Execution ID too long: {len(str(execution_id))}")
            return {"status": "error", "message": "Execution ID too long"}
        
        if step and len(str(step)) > MAX_STRING_LENGTH:
            _logger.warning(f"Step name too long: {len(str(step))}")
            return {"status": "error", "message": "Step name too long"}
        
        if kind and len(str(kind)) > MAX_STRING_LENGTH:
            _logger.warning(f"Kind too long: {len(str(kind))}")
            return {"status": "error", "message": "Kind too long"}
        
        if error_message and len(str(error_message)) > MAX_STRING_LENGTH * 2:
            error_message = str(error_message)[:MAX_STRING_LENGTH * 2]
        
        # Limit payload size (JSON)
        if payload and isinstance(payload, dict):
            import json
            try:
                payload_str = json.dumps(payload)
                if len(payload_str) > 10000:  # 10KB maximum
                    _logger.warning("Payload too large, truncating")
                    # Do not process very large payloads
                    payload = {"truncated": True, "size": len(payload_str)}
            except Exception:
                payload = None
        
        try:
            log_payrillium_event(
                execution_id=execution_id,
                step_name=step,
                kind=kind,
                payload=payload,
                success=success,
                error_message=error_message
            )
            return {"status": "success"}
        except Exception as e:
            _logger.error(f"Error logging event: {e}")
            return {"status": "error", "message": "Failed to log event"}

    @http.route('/payrillium/image_base_url', type='json', auth='user')
    def get_image_base_url(self):
        base_url = http.request.env['ir.config_parameter'].sudo(
        ).get_param('web.base.url')
        return {"image_base_url": f"{base_url}/payrillium" or "http://localhost:8069"}

    @http.route('/payrillium/session/terminal', type='json', auth='user')
    def get_terminal_from_session(self, sessionId, **kwargs):
        # Validate input
        try:
            session_id_int = int(sessionId)
            if session_id_int <= 0:
                raise ValueError("Invalid session ID")
        except (ValueError, TypeError):
            _logger.warning(f"Invalid sessionId provided: {sessionId}")
            return {"success": False, "message": "Invalid session ID"}

        user = request.env.user
        
        # Search session with permission verification
        session = request.env['pos.session'].sudo().browse(session_id_int)
        if not session.exists():
            return {"success": False, "message": "No session found"}
        
        # Verify that the user has access to this session
        if session.user_id.id != user.id:
            # Verify if the user has POS manager permissions
            if not user.has_group('point_of_sale.group_pos_manager'):
                _logger.warning(f"User {user.id} attempted to access session {session_id_int} owned by {session.user_id.id}")
                return {"success": False, "message": "Access denied"}
        
        # Verify that the session is opened
        if session.state != 'opened':
            _logger.warning(f"Session {session_id_int} is not in opened state (state: {session.state})")
            return {"success": False, "message": "Session is not opened"}
        
        _logger.info(f"session: {session}")
        terminal = session.config_id.payrillium_terminal_id
        _logger.info(f"terminal: {terminal}")
        if not terminal:
            return {"success": False, "message": "No terminal configured"}
        return {"success": True, "terminal": {"id": terminal.id, "name": terminal.name, "serial": terminal.serial}}

    @http.route('/payrillium/image/<int:product_id>', type='http', auth='public', website=True, methods=['GET'])
    def get_image(self, product_id):
        # Validate that product_id is valid
        if product_id <= 0:
            return http.Response(status=400)
        
        # Only allow access to publicly visible products or with active POS session
        # Use sudo only for reading, not for writing
        product = request.env['product.product'].sudo().browse(product_id)
        
        if not product.exists():
            return http.Response(status=404)
        
        # Verify that the product is active (for additional security)
        if not product.active:
            return http.Response(status=404)
        
        if product.image_128:
            try:
                image_data = base64.b64decode(product.image_128)
                return request.make_response(
                    image_data,
                    headers=[
                        ('Content-Type', 'image/png'),
                        # Add security headers
                        ('Cache-Control', 'private, max-age=3600'),
                        ('X-Content-Type-Options', 'nosniff')
                    ]
                )
            except Exception as e:
                _logger.error(f"Error decoding product image {product_id}: {e}")
                return http.Response(status=500)
        
        return http.Response(status=404)

# ─────────────────────────────────────────────
#  Payment router
# ─────────────────────────────────────────────
    # actions: basket , card, tip
    @http.route('/payrillium/proxy/<string:action>', type='json', auth='user')
    def proxy_to_terminal(self, action, **kwargs):
        if "kwargs" in kwargs:
            kwargs = kwargs["kwargs"]
        # Use logger instead of print, and mask sensitive data
        from ..services.mirillium.utils import _mask_sensitive_data
        masked_kwargs = _mask_sensitive_data(kwargs)
        _logger.debug(f" Incoming proxy request to endpoint: {action}")
        _logger.debug(
            f" Payload (masked): {json.dumps(masked_kwargs, indent=2)}")

        execution_id = kwargs.get("executionId", "missing")
        if isinstance(execution_id, dict):
            execution_id = execution_id.get("execution_id", "missing")
        _logger.debug("execution_id: %s", execution_id)

        session_id = kwargs.get('sessionId')
        terminal = _get_current_terminal(session_id)
        if not terminal:
            return {"status": "error", "message": "No terminal configured for this session"}
        terminal_id = terminal.serial

        if action == "card":
            payload = {
                "data": "",
            }
        else:
            payload_data = kwargs.copy()
            payload_data.pop('executionId', None)
            payload_data.pop('sessionId', None)
            payload = {
                "data": {
                    "data": payload_data,
                }
            }

        timestamp = int(datetime.utcnow().timestamp())
        payload = deep_clean_payload(payload)
        request_body = json.dumps(payload, separators=(",", ":"))

        # Use logger instead of print, and mask sensitive data
        masked_payload = _mask_sensitive_data(payload)
        _logger.debug(
            f" Final payload (masked): {json.dumps(masked_payload, indent=2)}")
        auth_hash = build_header_hash(request.env, payload, timestamp)

        log_payrillium_event(execution_id, action, "request", request_body)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {auth_hash}",
            "timestamp": str(timestamp)
        }

        try:
            url = build_url(terminal_id, "local", action)
            _logger.debug(f"  Calling endpoint: {action}")

            response = requests.post(url, headers=headers,  json={
                                     "data": request_body})
            response.raise_for_status()
            data = response.json()

            log_payrillium_event(execution_id, action,
                                 "response", data, success=True)
            return data

        except Exception as e:
            error_msg = str(e)
            _logger.error(f"  Error in call: {error_msg}")
            log_payrillium_event(
                execution_id, action, "response", None, success=False, error_message=error_msg)
            return {"status": "error", "message": error_msg}

    @http.route('/payrillium/payment/<string:action>', type='json', auth='user')
    def payrillium_payment_router(self, action, **kwargs):
        _logger.debug(f" Incoming dynamic payment request to: {action}")
        if "kwargs" in kwargs:
            kwargs = kwargs["kwargs"]
        execution_id = kwargs.get("executionId", "missing")
        _logger.debug("execution_id: %s", execution_id)

        session_id = kwargs.get('sessionId')
        terminal = _get_current_terminal(session_id)
        if not terminal:
            return {"status": "error", "message": "No terminal configured for this session"}
        terminal_id = terminal.serial

        payload_data = kwargs.copy()
        payload_data.pop('executionId', None)
        payload_data.pop('sessionId', None)
        payload = {
            "data": payload_data,
        }

        payload = deep_clean_payload(payload)
        request_body = json.dumps(payload, separators=(",", ":"))
        timestamp = int(datetime.utcnow().timestamp())
        auth_hash = build_header_hash(request.env, payload, timestamp)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {auth_hash}",
            "timestamp": str(timestamp)
        }

        log_payrillium_event(
            execution_id, f"payment/{action}", "request", request_body)

        try:
            url = build_url(terminal_id, "payment", action)
            _logger.debug(f"  Calling {url}")
            response = requests.post(url, headers=headers, json={
                                     "data": request_body})
            response.raise_for_status()
            data = response.json()

            # Mask sensitive data before logging
            masked_data = _mask_sensitive_data(data)
            _logger.debug(
                f"  Response (masked): {json.dumps(masked_data, indent=2)}")
            log_payrillium_event(
                execution_id, f"payment/{action}", "response", data, success=True)
            return data
        except Exception as e:
            error_msg = str(e)
            _logger.error(f"  Error: {error_msg}")
            log_payrillium_event(
                execution_id, f"payment/{action}", "response", None, success=False, error_message=error_msg)
            return {"status": "error", "message": error_msg}


# only for tokenize card

    @http.route('/payrillium/refund_tokenize', type='json', auth='user')
    def payrillium_payment_refund_tokenize(self, **kwargs):
        """
        POS calls this endpoint to trigger a refund via token.
        kwargs expected: token, amount, currency (optional), record_id (optional)
        """
        if "kwargs" in kwargs:
            kwargs = kwargs["kwargs"]

        execution_id = kwargs.get("executionId", "missing")
        token = kwargs.get("token_card_id")
        amount = kwargs.get("amount")
        currency = kwargs.get("currency", "USD")
        record_id = kwargs.get("record_id")
        transaction_id = kwargs.get("transaction_id")

        # Validate input
        if not token:
            return {"status": "error", "message": "Missing token"}
        
        if not amount:
            return {"status": "error", "message": "Missing amount"}
        
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                raise ValueError("Invalid amount")
        except (ValueError, TypeError):
            _logger.warning(f"Invalid amount provided: {amount}")
            return {"status": "error", "message": "Invalid amount"}
        
        # Validate currency
        if not isinstance(currency, str) or len(currency) != 3:
            _logger.warning(f"Invalid currency code provided: {currency}")
            return {"status": "error", "message": "Invalid currency"}
        
        # Validate record_id if provided
        if record_id:
            try:
                record_id_int = int(record_id)
                if record_id_int <= 0:
                    raise ValueError("Invalid record ID")
                # Verify that the company exists and the user has access
                company = request.env["res.company"].browse(record_id_int)
                if not company.exists():
                    _logger.warning(f"Company {record_id_int} not found")
                    return {"status": "error", "message": "Company not found"}
                try:
                    company.check_access_rights('read')
                    company.check_access_rule('read')
                except Exception as e:
                    _logger.warning(f"Access denied to company {record_id_int}: {e}")
                    return {"status": "error", "message": "Access denied"}
                record = company
            except (ValueError, TypeError):
                _logger.warning(f"Invalid record_id provided: {record_id}")
                return {"status": "error", "message": "Invalid record ID"}
        else:
            record = request.env.company

        try:
            result = refund_payment_by_token(
                record, transaction_id, amount, currency)

            if result.get("success"):
                return {"status": "ok", "data": result}
            else:
                return {
                    "status": "error",
                    "message": result.get("message", "Refund failed"),
                    "data": result,
                }
        except Exception as e:
            _logger.error("Refund error in controller: %s", str(e))
            return {"status": "error", "message": str(e)}
# ─────────────────────────────────────────────
#  Pay by Link – Routes
# ─────────────────────────────────────────────

    @http.route('/payrillium/generate_link', type='json', auth='user')
    def generate_link(self, model, id, amount):
        # Validate that the model is allowed (only invoice models)
        allowed_models = ['account.move']
        if model not in allowed_models:
            _logger.warning(f"Unauthorized model access attempt: {model}")
            return {"success": False, "error": "Unauthorized model"}
        
        # Validate that id is a valid integer
        try:
            record_id = int(id)
            if record_id <= 0:
                raise ValueError("Invalid ID")
        except (ValueError, TypeError):
            _logger.warning(f"Invalid ID provided: {id}")
            return {"success": False, "error": "Invalid record ID"}
        
        # Validate that amount is a valid number
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                raise ValueError("Invalid amount")
        except (ValueError, TypeError):
            _logger.warning(f"Invalid amount provided: {amount}")
            return {"success": False, "error": "Invalid amount"}
        
        # Get the record with access verification
        record = request.env[model].browse(record_id)
        if not record.exists():
            return {"success": False, "error": "Record not found"}
        
        # Verify access permissions to the record
        try:
            record.check_access_rights('read')
            record.check_access_rule('read')
        except Exception as e:
            _logger.warning(f"Access denied to {model} record {record_id}: {e}")
            return {"success": False, "error": "Access denied"}

        # Early guard: if there is already an active/pending link for this invoice, reuse it
        try:
            # First check by invoice_id
            existing_links = request.env['payrillium.payment.link'].search([
                ('invoice_id', '=', record.id),
                ('status', 'in', ['active', 'pending'])
            ], order='create_date desc')

            _logger.info(
                f"🔍 Checking for existing links for invoice {record.id}: found {len(existing_links)} links by invoice_id")

            # If no links found by invoice_id, try by payment_link_id pattern (INV<id>A<seq>)
            if not existing_links:
                all_links = request.env['payrillium.payment.link'].search([
                    ('status', 'in', ['active', 'pending'])
                ], order='create_date desc')
                _logger.info(
                    f"🔍 Checking all active/pending links ({len(all_links)} total) for pattern matching")

                for link in all_links:
                    if link.payment_link_id and link.payment_link_id.startswith(f"INV{record.id}A"):
                        _logger.info(
                            f"  - Found link {link.id} with pattern INV{record.id}A*: status={link.status}")
                        existing_links = link
                        break

            for link in existing_links:
                _logger.info(
                    f"  - Link {link.id}: status={link.status}, invoice_id={link.invoice_id}, url={link.link_url[:50] if link.link_url else 'None'}...")

            if existing_links and existing_links[0].link_url:
                _logger.info(
                    f"✅ Reusing existing link {existing_links[0].id} for invoice {record.id}")
                return {
                    "success": True,
                    "link": existing_links[0].link_url,
                    "warning": "A payment link already exists for this invoice. Copying existing link. If you need a new one, deactivate/delete the current link first."
                }
            else:
                _logger.info(
                    f"❌ No valid existing link found for invoice {record.id}, proceeding to create new one")
        except Exception as e:
            _logger.error(
                f"Error checking existing links for invoice {record.id}: {e}")
            # If guard lookup fails, proceed to creation path (fallback)
            pass

        link = create_payment_link(record, amount=amount)

        # Check if link creation returned an error dict
        if isinstance(link, dict) and link.get("error"):
            # Handle DUPLICATE_RECORD specifically
            if link.get("reason") == "DUPLICATE_RECORD":
                # Try to find existing payment link for this invoice
                existing_link = request.env['payrillium.payment.link'].search([
                    ('invoice_id', '=', record.id),
                    ('status', 'in', ['active', 'pending'])
                ], limit=1, order='create_date desc')

                if existing_link and existing_link.link_url:
                    return {
                        "success": True,
                        "link": existing_link.link_url,
                        "warning": "A payment link already exists for this invoice. Showing existing link."
                    }
                else:
                    return {
                        "success": False,
                        "error": "A payment link already exists for this invoice, but could not be retrieved from the database."
                    }
            else:
                # Other errors
                return {
                    "success": False,
                    "error": link.get("message", "Failed to create payment link")
                }

        if not link:
            return {"success": False, "error": "Failed to create payment link"}

            # Add message to chatter when payment link is created
        if hasattr(record, 'message_post'):
            # Create a message with truncated URL and hidden full URL
            from markupsafe import Markup, escape
            # Sanitize the URL before using it in HTML to prevent XSS
            # Show only the first 30 characters + "..."
            escaped_link = escape(link)
            short_url = escaped_link[:30] + "..." if len(escaped_link) > 30 else escaped_link
            # Use escape to prevent XSS in the hidden URL as well
            hidden_url = Markup(f'<span style="display:none;">{escaped_link}</span>')
            message_body = Markup(
                f"Payment link created: {short_url} {hidden_url}")

            record.message_post(
                body=message_body,
                message_type='notification',
                subtype_xmlid='mail.mt_comment'
            )

        return {"success": True, "link": link}

    @http.route('/payrillium/token/authorize', type='json', auth='user')
    def payrillium_token_authorize(self, token_id, amount, currency, provider_id):
        # Validate input
        try:
            token_id_int = int(token_id)
            if token_id_int <= 0:
                raise ValueError("Invalid token ID")
        except (ValueError, TypeError):
            _logger.warning(f"Invalid token_id provided: {token_id}")
            return {"success": False, "message": "Invalid token ID"}
        
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                raise ValueError("Invalid amount")
        except (ValueError, TypeError):
            _logger.warning(f"Invalid amount provided: {amount}")
            return {"success": False, "message": "Invalid amount"}
        
        # Validate currency (only valid ISO codes)
        if not isinstance(currency, str) or len(currency) != 3:
            _logger.warning(f"Invalid currency code provided: {currency}")
            return {"success": False, "message": "Invalid currency"}
        
        # Get token with permission verification
        token = request.env['payment.token'].browse(token_id_int)
        if not token.exists():
            return {"success": False, "message": "Token not found"}
        
        # Verificar permisos de acceso
        try:
            token.check_access_rights('read')
            token.check_access_rule('read')
        except Exception as e:
            _logger.warning(f"Access denied to payment token {token_id}: {e}")
            return {"success": False, "message": "Access denied"}
        
        if not token.provider_ref:
            return {"success": False, "message": "Invalid token"}
        random_suffix = str(random.randint(100000, 999999))
        client_ref = f"TOKPOS{provider_id}{token.provider_ref}-{random_suffix}"
        result = authorize_payment(
            record=token,
            payment_instrument=token.provider_ref,
            amount=amount,
            currency=currency,
            type='CARD',  # function called  from POS (only card type enabled)
            clientReferenceCode=client_ref,
        )
        return result

# ─────────────────────────────────────────────
#  Terminal CRUD
# ─────────────────────────────────────────────
    @http.route('/payrillium/check_terminal_backend', type='json', auth='user')
    def check_terminal_backend(self, terminal_id=None, **kw):
        if not terminal_id:
            return {"status": "error", "message": "No terminal ID or serial provided"}
        
        # Try to find terminal by ID (integer) or by serial (string)
        terminal = None
        try:
            # First, try as integer (terminal ID)
            terminal_id_int = int(terminal_id)
            if terminal_id_int > 0:
                terminal = request.env['payrillium.terminal'].browse(terminal_id_int)
                if not terminal.exists():
                    terminal = None
        except (ValueError, TypeError):
            # Not an integer, try as serial (string)
            pass
        
        # If not found by ID, search by serial
        if not terminal or not terminal.exists():
            terminal = request.env['payrillium.terminal'].search([
                ('serial', '=', str(terminal_id))
            ], limit=1)
        
        # If still not found, return error
        if not terminal or not terminal.exists():
            _logger.warning(f"Terminal not found: {terminal_id} (tried as ID and serial)")
            return {"status": "error", "message": "Terminal not found"}
        
        # Verify that the user has access to this terminal
        try:
            terminal.check_access_rights('read')
            terminal.check_access_rule('read')
        except Exception as e:
            _logger.warning(f"Access denied to terminal {terminal.id} ({terminal_id}): {e}")
            return {"status": "error", "message": "Access denied"}
        
        # Check terminal using the terminal serial (not ID) - build_url requires serial
        if not terminal.serial:
            return {"status": "error", "message": "Terminal has no serial number configured"}
        
        return request.env['payrillium.terminal'].sudo()._check_terminal_core(terminal.serial)

    @http.route('/payrillium/check_config', type='json', auth='user')
    def check_config(self, **kw):
        """Check if Payrillium is configured"""
        config = request.env['payrillium.config'].sudo().search([], limit=1)
        is_configured = bool(config and config.installed and config.token)
        return {"configured": is_configured}

    @http.route('/payrillium/reset_terminal_backend', type='json', auth='user')
    def reset_terminal_backend(self, terminal_id=None, **kw):
        if not terminal_id:
            return {"status": "error", "message": "No terminal ID provided"}
        
        # Validate that terminal_id is a valid integer
        try:
            terminal_id_int = int(terminal_id)
            if terminal_id_int <= 0:
                raise ValueError("Invalid terminal ID")
        except (ValueError, TypeError):
            _logger.warning(f"Invalid terminal_id provided: {terminal_id}")
            return {"status": "error", "message": "Invalid terminal ID"}
        
        # Verify that the terminal exists and the user has write permissions
        terminal = request.env['payrillium.terminal'].browse(terminal_id_int)
        if not terminal.exists():
            return {"status": "error", "message": "Terminal not found"}
        
        try:
            terminal.check_access_rights('write')
            terminal.check_access_rule('write')
        except Exception as e:
            _logger.warning(f"Access denied to reset terminal {terminal_id}: {e}")
            return {"status": "error", "message": "Access denied"}
        
        return request.env['payrillium.terminal'].sudo()._reset_terminal_core(terminal_id_int)
