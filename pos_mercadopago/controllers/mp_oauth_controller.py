# -*- coding: utf-8 -*-

import logging
import json
import requests
from odoo import http, fields
from odoo.http import request

_logger = logging.getLogger(__name__)


class MPOAuthController(http.Controller):
    
    @http.route('/mercadopago/oauth/callback', type='http', auth='public', methods=['GET', 'POST'], csrf=False)
    def oauth_callback(self, **kwargs):
        """
        Handle MercadoPago OAuth callback
        - GET: Receive authorization code from MercadoPago redirect
        - POST: Process token exchange request
        """
        
        # Handle POST request for token exchange
        _logger.info(f"Authorization callback - Code: {request.httprequest.method}")
        if request.httprequest.method == 'POST':
            return request.make_response(
                json.dumps({'success': True, 'message': 'Token data updated successfully'}),
                headers={'Content-Type': 'application/json'}
            )
        
        # Handle GET request for authorization callback
        return self._handle_authorization_callback(kwargs)
    
    def _handle_authorization_callback(self, kwargs):
        """Handle GET request from MercadoPago authorization redirect"""
        code = kwargs.get('code')
        state = kwargs.get('state')
        error = kwargs.get('error')

        _logger.info(f"Authorization callback - Code: {code}, State: {state}, Error: {error}")

        if error:
            error_description = kwargs.get('error_description', 'Unknown error')
            _logger.error(f"OAuth error: {error} - {error_description}")
            return f"""
            <html>
                <body>
                    <h2>Error de Autorización</h2>
                    <p>Error: {error}</p>
                    <p>Descripción: {error_description}</p>
                    <p>Por favor, cierre esta ventana e intente nuevamente.</p>
                </body>
            </html>
            """
        
        if not code or not state:
            _logger.error("Missing code or state in OAuth callback")
            return """
            <html>
                <body>
                    <h2>Error de Autorización</h2>
                    <p>Faltan parámetros requeridos en la respuesta de autorización.</p>
                    <p>Por favor, cierre esta ventana e intente nuevamente.</p>
                </body>
            </html>
            """
        
        # Find credential by state
        try:
            credential = request.env['mp.credential'].sudo().search([('state', '=', state)], limit=1)
            if not credential:
                _logger.error(f"No credential found for state: {state}")
                return """
                <html>
                    <body>
                        <h2>Error de Autorización</h2>
                        <p>Parámetro de estado inválido. No se encontró la credencial correspondiente.</p>
                        <p>Por favor, cierre esta ventana e intente nuevamente desde Odoo.</p>
                    </body>
                </html>
                """
            
            # Update authorization code
            credential.authorization_code = code
            _logger.info(f"Authorization code received for credential: {credential.name}")
            
            return f"""
            <html>
                <body>
                    <h2>Autorización Exitosa</h2>
                    <p>Se ha recibido el código de autorización para la credencial: <strong>{credential.name}</strong></p>
                    <p>Ahora puede cerrar esta ventana y volver a Odoo para completar el intercambio de tokens.</p>
                    <p><strong>Siguiente paso:</strong> Haga clic en el botón «2. Intercambiar Código» en el formulario de credenciales.</p>
                    <script>
                        setTimeout(function() {{
                            window.close();
                        }}, 5000);
                    </script>
                </body>
            </html>
            """
            
        except Exception as e:
            _logger.error(f"Error processing OAuth callback: {str(e)}")
            return """
            <html>
                <body>
                    <h2>Error de Autorización</h2>
                    <p>Se ha producido un error al procesar la autorización.</p>
                    <p>Cierre esta ventana e inténtelo de nuevo.</p>
                </body>
            </html>
            """