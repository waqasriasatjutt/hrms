# -*- coding: utf-8 -*-
# Copyright (C) 2024 Axcelere.
# Licensed under the GPL-3.0 License or later.

from odoo import models, fields, api
import requests
import time
from odoo.addons.pos_payway.models.payway_library import PROD_BASE_API_URL, TEST_BASE_API_URL, BASE_PATH_SETTLEMENTS
import logging
_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    access_token = fields.Char(string="Access token", readonly=True, copy=False)
    api_key = fields.Char(string="Api Key", readonly=True, copy=False)
    allow_payway_terminal = fields.Boolean(string="Terminal Payway")
    settlement = fields.Boolean(string="Settlement", compute='_make_settlement', store=True)
    payway_token_updating = fields.Datetime(string='Fecha del actualizacion del token', readonly=True, copy=False)

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        new_model = 'pos.order'
        if new_model not in result:
            result.append(new_model)
        return result

    def _ensure_valid_token(self):
        """
        Asegura que el token de Payway sea válido, renovándolo si es necesario.

        El token se renueva si:
        - No existe fecha de actualización previa
        - Han pasado 55+ minutos desde la última actualización (margen de seguridad de 5 min)

        Returns:
            bool: True si el token fue renovado, False si aún es válido
        """
        self.ensure_one()
        current_time = fields.Datetime.now()
        token_update_time = self.payway_token_updating

        # Tiempo de expiración: 55 minutos (3300 segundos) - margen de 5 minutos
        TOKEN_EXPIRY_SECONDS = 3300

        # Si no hay fecha de actualización o han pasado 55+ minutos
        if not token_update_time:
            _logger.info('Token de Payway no inicializado para config "%s". Obteniendo nuevo token...', self.name)
            self._get_payway_token()
            return True

        time_diff_seconds = (current_time - token_update_time).total_seconds()

        if time_diff_seconds >= TOKEN_EXPIRY_SECONDS:
            minutes_elapsed = time_diff_seconds / 60
            _logger.info(
                'Token de Payway expirado para config "%s" (%.1f minutos desde última actualización). Renovando...',
                self.name, minutes_elapsed
            )
            self._get_payway_token()
            return True

        # Token aún válido
        minutes_remaining = (TOKEN_EXPIRY_SECONDS - time_diff_seconds) / 60
        _logger.debug('Token de Payway válido para config "%s". Tiempo restante: %.1f minutos',
                     self.name, minutes_remaining)
        return False

    @api.depends('session_ids', 'session_ids.state')
    def _make_settlement(self):
        for pos_config in self:
            if pos_config.current_session_state == 'closing_control' and not pos_config.settlement:
                # Buscar TODOS los métodos de pago Payway asociados a este POS
                pos_payment_methods = self.env['pos.payment.method'].search([
                    ('use_payment_terminal', '=', 'payway'),
                    ('config_ids', 'in', [pos_config.id])
                ])

                if not pos_payment_methods:
                    _logger.warning("No se encontraron métodos de pago con terminal Payway para la configuración: %s",
                                    pos_config.name)
                    continue
                
                # Verificar y actualizar token si es necesario
                pos_config._ensure_valid_token()

                access_token = pos_config.access_token or ''
                if not access_token:
                    _logger.warning("Token de acceso no configurado para el POS: %s", pos_config.name)
                    continue

                # Contador de cierres exitosos
                successful_settlements = 0
                total_terminals = len(pos_payment_methods)

                _logger.info("Iniciando cierre de lote para %d terminal(es) Payway en POS '%s'",
                           total_terminals, pos_config.name)

                # Procesar cada terminal Payway
                for pos_payment_method_id in pos_payment_methods:
                    terminal_id = pos_payment_method_id.payway_terminal_number

                    # Validar terminal_id
                    if not terminal_id:
                        _logger.warning("ID de terminal Payway no configurado para método de pago: %s",
                                      pos_payment_method_id.name)
                        continue

                    # Determinar entorno (test/prod)
                    url = TEST_BASE_API_URL if pos_payment_method_id.payway_test_mode else PROD_BASE_API_URL

                    # Datos requeridos para la llamada API
                    cuit_cuil = pos_payment_method_id.company_id.vat
                    subnet_acquirer_id = pos_payment_method_id.pos_payway_config_id.payway_acquier_id
                    print_receipt = True

                    # Construir URL
                    url = (
                            url +
                            BASE_PATH_SETTLEMENTS +
                            f'?cuit_cuil={cuit_cuil}&subnet_acquirer_id={subnet_acquirer_id}'
                            f'&terminal_id={terminal_id}&print_receipt={print_receipt}'
                    )

                    headers = {'Authorization': f'Bearer {access_token}'}

                    try:
                        _logger.info("Cerrando lote para terminal Payway: %s", terminal_id)
                        response = requests.request("POST", url, headers=headers, timeout=30)

                        # Registrar log
                        self.env['payway.log'].sudo().create_logs(
                            pos_config.current_session_id,
                            'box_closed',
                            headers,
                            url,
                            response.status_code,
                            '',
                            response.json()
                        )

                        if response.status_code == 200:
                            successful_settlements += 1
                            _logger.info("Cierre de lote exitoso para terminal: %s", terminal_id)
                        else:
                            _logger.error('Error en cierre de arqueo para terminal %s. Código: %s. Respuesta: %s',
                                        terminal_id, response.status_code, response.text)
                    except requests.exceptions.RequestException as e:
                        _logger.exception('Excepción al intentar cerrar arqueo con Payway para terminal %s: %s',
                                        terminal_id, str(e))
                    except ValueError as e:  # JSON decode error
                        _logger.exception('Respuesta no JSON válida de Payway para terminal %s: %s',
                                        terminal_id, str(e))

                # Marcar settlement como True solo si todos los cierres fueron exitosos
                if successful_settlements == total_terminals:
                    pos_config.settlement = True
                    _logger.info("Cierre de lote completado exitosamente para todas las terminales (%d/%d) en POS '%s'",
                               successful_settlements, total_terminals, pos_config.name)
                else:
                    _logger.warning("Cierre de lote parcial: %d/%d terminales cerradas exitosamente en POS '%s'",
                                  successful_settlements, total_terminals, pos_config.name)

    def _get_payway_token(self, retry=True):
        """
        Obtiene un nuevo token de acceso desde la API de Payway.

        Args:
            retry (bool): Si es True, reintentará una vez en caso de error de conexión

        Returns:
            bool: True si el token fue obtenido exitosamente, False en caso contrario
        """
        for pos_config in self:
            # Buscar el método de pago Payway
            pos_payment_method = self.env['pos.payment.method'].search(
                [('use_payment_terminal', '=', 'payway')], limit=1
            )
            if not pos_payment_method:
                _logger.warning("No se encontró un método de pago con terminal Payway para config '%s'.",
                              pos_config.name)
                return False

            # Determinar la URL según el modo de prueba
            base_url = TEST_BASE_API_URL if pos_payment_method.payway_test_mode else PROD_BASE_API_URL
            url = f"{base_url}/v1/oauth/accesstoken?grant_type=client_credentials"

            # Preparar headers
            auth_secret = pos_payment_method.pos_payway_config_id.payway_secret_basic
            headers = {'Authorization': auth_secret} if auth_secret else {}

            if not auth_secret:
                _logger.error("No se encontró el secreto de autenticación para Payway en config '%s'.",
                            pos_config.name)
                return False

            # Log y solicitud
            _logger.info('Solicitando token de Payway para config "%s"...', pos_config.name)
            try:
                response = requests.get(url, headers=headers, timeout=10)
            except requests.exceptions.RequestException as e:
                _logger.error("Error al conectarse a Payway para config '%s': %s", pos_config.name, e)
                # Retry logic: intentar una vez más después de 2 segundos
                if retry:
                    _logger.info("Reintentando obtener token de Payway en 2 segundos...")
                    time.sleep(2)
                    return pos_config._get_payway_token(retry=False)
                return False

            if response.status_code == 200:
                try:
                    data = response.json()
                    access_token = data.get('access_token')
                    api_key = data.get('apiKey')

                    if not access_token or not api_key:
                        _logger.error("Respuesta de Payway incompleta para config '%s': faltan campos requeridos.",
                                    pos_config.name)
                        return False

                    # Actualizar campos usando write para evitar problemas con campos readonly
                    pos_config.sudo().write({
                        'access_token': access_token,
                        'api_key': api_key,
                        'payway_token_updating': fields.Datetime.now()
                    })

                    # Si no es cierre de sesión, resetear settlement
                    if pos_config.current_session_state == 'opened':
                        pos_config.sudo().write({'settlement': False})

                    _logger.info(
                        'Token obtenido exitosamente para config "%s". Expira en ~60 minutos.',
                        pos_config.name
                    )
                    return True

                except ValueError as e:
                    _logger.error("Error al parsear la respuesta JSON de Payway para config '%s': %s",
                                pos_config.name, e)
                    return False
            else:
                _logger.error(
                    "Error al obtener token de Payway para config '%s'. Código: %s, Respuesta: %s",
                    pos_config.name, response.status_code, response.text
                )
                return False
        return False
