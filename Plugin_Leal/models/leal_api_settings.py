from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import requests
import json
import logging
from datetime import timedelta

_logger = logging.getLogger(__name__)

class LealApiSettings(models.Model):
    _name = 'leal.api.settings'
    _description = 'Leal API Settings'

    username = fields.Char(string='Usuario', required=True, 
        #help="Ingrese el usuario proporcionado por Leal."
    )
    password = fields.Char(string='Contraseña', required=True, 
        #help="Ingrese la contraseña porporcinada por Leal."
    )
    active = fields.Boolean(default=True, string='Estado')
    is_authenticated = fields.Boolean(string='Autenticado', default=False, readonly=True)
    last_auth_date = fields.Datetime(string='Última autenticación', readonly=True)
    
    # Campo para seleccionar ambiente
    is_production = fields.Boolean(
        string='Ambiente de Producción', 
        default=False, 
        # help="Marque esta casilla para usar el ambiente de producción. Desmarque para usar ambiente de pruebas."
    )
    
    # URL se calcula automáticamente según el ambiente
    api_url = fields.Char(
        string='URL de API', 
        compute='_compute_api_url', 
        store=True,
        readonly=True,
    )
    
    api_url_ct = fields.Char(
        string='URL de API CT', 
        compute='_compute_api_url_ct', 
        store=True,
        readonly=True,
    )
    
    # Campos para tokens
    access_token = fields.Text(string='Token de Acceso', readonly=True)
    refresh_token = fields.Text(string='Token de Renovación', readonly=True, help="Token para renovar la autenticación")
    token_expires_at = fields.Datetime(string='Token Expira', readonly=True, help="Fecha y hora de expiración del token")
    
    # campos para token 
    access_token_ct = fields.Text(string='Token de Acceso CT', readonly=True)
    refresh_token_ct = fields.Text(string='Token de Renovación CT', readonly=True, help="Token para renovar la autenticación")
    token_expires_at_ct = fields.Datetime(string='Token Expira CT', readonly=True, help="Fecha y hora de expiración del token")
    
    # Campo para permitir facturas en cero
    allow_zero_invoices = fields.Boolean(
        string='Permitir facturas en $0',
        default=False,
        help="Permite crear facturas con valor de $0 para productos de Leal Redeem"
    )
    hidden_characters = fields.Integer(
        string='Cantidad de caracteres ocultos', 
        help="Cantidad de caracteres ocultos para el código de redención campañas",
        default=4
    )
    
    def _valid_field_parameter(self, field, parameter):
        # Permitir el parámetro 'password' para el campo password
        if field.name == 'password' and parameter == 'password':
            return True
        return super()._valid_field_parameter(field, parameter)
    
    @api.depends('is_production')
    def _compute_api_url(self):
        """Calcula la URL de API según el ambiente seleccionado"""
        for record in self:
            if record.is_production:
                record.api_url = 'https://api.puntosleal.com/api'  # URL de producción
            else:
                record.api_url = 'https://testapi.puntosleal.com/api'  # URL de desarrollo
                
    @api.depends('is_production')
    def _compute_api_url_ct(self):
        """Calcula la URL de API según el ambiente seleccionado para promociones"""
        for record in self:
            if record.is_production:
                record.api_url_ct = 'https://api.leal.co'  # URL de producción
            else:
                record.api_url_ct = 'https://apiqa.leal.co'  # URL de desarrollo
    
    @api.onchange('is_production')
    def _onchange_is_production(self):
        """Actualiza la URL cuando cambia el ambiente y limpia la autenticación"""
        if self.is_production:
            self.api_url = 'https://api.puntosleal.com/api'
            self.api_url_ct = 'https://api.leal.co'
        else:
            self.api_url = 'https://testapi.puntosleal.com/api'
            self.api_url_ct = 'https://apiqa.leal.co'
        
        # Si cambia el ambiente, limpiar la autenticación para forzar re-autenticación
        if self.is_authenticated:
            self.is_authenticated = False
            self.access_token = False
            self.refresh_token = False
            self.token_expires_at = False
            self.last_auth_date = False
    
    @api.model_create_multi
    def create(self, vals_list):
        # Convertir vals a lista si no lo es (para compatibilidad)
        if not isinstance(vals_list, list):
            vals_list = [vals_list]
        
        # Validaciones para cada registro
        for vals in vals_list:
            existing_authenticated = self.search([('is_authenticated', '=', True)], limit=1)
            if existing_authenticated:
                raise UserError('Ya existe una configuración autenticada. Solo se permite una configuración autenticada activa.')
            
            existing_records = self.search([])
            if existing_records:
                raise UserError('Solo se permite una configuración de Leal API. Por favor, modifique la configuración existente.')
            
            vals['active'] = True
            vals['is_authenticated'] = False  # Nuevo registro no está autenticado
        
        return super().create(vals_list)
    
    def write(self, vals):
        if 'is_authenticated' in vals and self.env.context.get('from_authenticate_method') != True:
            vals.pop('is_authenticated')  # Solo se puede cambiar desde el método authenticate_api
        
        if vals.get('active'):
            self.search([('active', '=', True), ('id', 'not in', self.ids)]).write({'active': False})
            
        return super().write(vals)
    
    @api.constrains('is_authenticated')
    def _check_only_one_authenticated(self):
        """Asegurar que solo hay una configuración autenticada"""
        authenticated_configs = self.search([('is_authenticated', '=', True)])
        if len(authenticated_configs) > 1:
            raise ValidationError('Solo puede haber una configuración autenticada a la vez.')
    
    def authenticate_api(self):
        """Método para autenticar contra la API externa"""
        for record in self:
            if not record.username or not record.password:
                raise UserError('Por favor, ingrese usuario y contraseña antes de autenticar.')
            
            try:
                # Preparar los datos de autenticación según el formato de Leal API
                auth_data = {
                    'usuario': record.username,
                    'contrasena': record.password
                }
                
                headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
                
                response = requests.post(record.api_url + '/com_usuarios/login', 
                                        data=json.dumps(auth_data), 
                                        headers=headers, 
                                        timeout=30)
                response.raise_for_status()
                result = response.json()
                
                if result.get('code') == 100:
                    data = result.get('data', {})
                    access_token = data.get('token', '')
                    refresh_token = data.get('refresh_token', '')
                    expires_at = fields.Datetime.now() + timedelta(minutes=1)
                    
                    auth_token_ct = result.get('authTokenCt', {})
                    data_ct = auth_token_ct.get('data', {})
                    access_token_ct = data_ct.get('AccessToken', '')
                    refresh_token_ct = data_ct.get('RefreshToken', '')
                    expires_at_ct = fields.Datetime.now() + timedelta(minutes=1)
                    
                    record.write({
                        'is_authenticated': True,
                        'last_auth_date': fields.Datetime.now(),
                        'access_token': access_token,
                        'refresh_token': refresh_token,
                        'token_expires_at': expires_at,
                        'access_token_ct': access_token_ct,
                        'refresh_token_ct': refresh_token_ct,
                        'token_expires_at_ct': expires_at_ct,
                    })
                    
                    _logger.info(f"Autenticación exitosa para usuario: {record.username}. Token guardado.")
                    
                    try:
                        api_client = self.env['leal.api.client']
                        user_data_result = api_client.get_user_data_after_auth(record.id)
                        
                        message = f'Autenticación exitosa. Token guardado y datos del usuario obtenidos.'
                        if user_data_result.get('success'):
                            message += f' Usuario: {user_data_result.get("data", {}).get("user", {}).get("nombre", "N/A")}'
                    except Exception as e:
                        _logger.warning(f"Error al obtener datos del usuario después de autenticación: {str(e)}")
                        message = f'Autenticación exitosa, pero no se pudieron obtener los datos del usuario: {str(e)}'
                    
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': 'Autenticación Exitosa',
                            'message': message,
                            'type': 'success',
                            'sticky': False,
                        }
                    }
                else:
                    record.write({'is_authenticated': False})
                    error_message = result.get('message', 'Credenciales inválidas')
                    raise UserError(f"Error de autenticación: {error_message}")
                    
            except requests.exceptions.RequestException as e:
                _logger.error(f"Error de conexión con la API: {str(e)}")
                record.write({'is_authenticated': False})
                raise UserError(f"Error de conexión con la API: {str(e)}")
            except Exception as e:
                _logger.error(f"Error durante la autenticación: {str(e)}")
                record.write({'is_authenticated': False})
                raise UserError(f"Error durante la autenticación: {str(e)}")
    
    def get_valid_token(self, type: str = None):
        """Obtiene un token válido, renovándolo si es necesario"""
        self.ensure_one()
        
        # Verificar si el token actual es válido
        if not self.access_token:
            raise UserError('No hay token de autenticación. Por favor, autentíquese primero.')
        
        # Verificar si el token ha expirado
        if self.token_expires_at and fields.Datetime.now() >= self.token_expires_at:
            _logger.info(f"Token expirado para usuario: {self.username}. Intentando renovar...")
            
            # Intentar renovar el token usando refresh_token
            if self.refresh_token:
                try:
                    self._refresh_token()
                except Exception as e:
                    _logger.error(f"Error renovando token: {str(e)}")
                    # Si no se puede renovar, re-autenticar
                    self.authenticate_api()
            else:
                # Si no hay refresh_token, re-autenticar
                self.authenticate_api()
        return self.access_token if type == None else self.access_token_ct
    
    def _refresh_token(self):
        """Renueva el token usando refresh_token"""
        self.ensure_one()
        _logger.info(f"Renovando token para usuario: {self.username}")
        self.authenticate_api()
        return
        ## Se cambia la función para volverse a autenticar y no usar el refresh token. 
        # if not self.refresh_token:
        #     raise UserError('No hay refresh token disponible.')
        
        # # Obtener datos del usuario para incluir id_cms e id_sucursal
        # user_data = self.get_user_data()
        # if not user_data:
        #     raise UserError('No se encontraron datos del usuario. No se puede renovar el token.')
        
        # refresh_data = {
        #     'refresh_token': self.refresh_token,
        #     'uid_cms': user_data.uid_cms,
        #     'id_sucursal': user_data.id_sucursal
        # }
        # _logger.info(f"Renovando token para usuario: {self.username}")
        # data_token = self._generate_new_access_token(refresh_data)
        # self.write({
        #     'access_token': data_token.get('access_token', ''),
        #     'refresh_token': data_token.get('refresh_token', ''),
        #     'token_expires_at': data_token.get('token_expires_at', ''),
        #     'last_auth_date': fields.Datetime.now()
        # })
        
        # if self.access_token_ct and self.refresh_token_ct:
        #     # Renovar también el token CT si existe
        #     refresh_data_ct = {
        #         'refresh_token': self.refresh_token_ct,
        #         'uid_cms': user_data.uid_cms,
        #         'id_sucursal': user_data.id_sucursal
        #     }
        #     _logger.info(f"Renovando token CT para usuario: {self.username}")
        #     data_token_ct = self._generate_new_access_token(refresh_data_ct)
        #     self.write({
        #         'access_token_ct': data_token_ct.get('access_token', ''),
        #         'refresh_token_ct': data_token_ct.get('refresh_token', ''),
        #         'token_expires_at_ct': data_token_ct.get('token_expires_at', ''),
        #         'last_auth_date': fields.Datetime.now()
        #     })
        # else:
        #     _logger.info("No se encontraron tokens CT para renovar.")

    def _generate_new_access_token(self, refresh_data: str):
        try:
                        
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            # Hacer petición para renovar token
            response = requests.post(self.api_url + '/com_usuarios/refresh_token', 
                                   data=json.dumps(refresh_data), 
                                   headers=headers, 
                                   timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if result['code'] == 100:
                new_token = result['token']
                new_refresh_token = result['refresh_token']
                
                # Actualizar tokens
                expires_at = fields.Datetime.now() + timedelta(minutes=1)
                
                return {
                    'access_token': new_token,
                    'refresh_token': new_refresh_token,
                    'token_expires_at': expires_at,
                    'last_auth_date': fields.Datetime.now()
                }
            else:
                raise Exception(f"Error renovando token: {result['code']}")
                
        except Exception as e:
            _logger.error(f"Error renovando token: {str(e)}")
            raise
    
    def is_token_valid(self):
        """Verifica si el token actual es válido"""
        self.ensure_one()
        
        if not self.access_token:
            return False
        
        if self.token_expires_at and fields.Datetime.now() >= self.token_expires_at:
            return False
            
        return True
    
    @api.model
    def get_active_config(self):
        """Obtiene la configuración activa"""
        config = self.search([('active', '=', True)], limit=1)
        if not config:
            raise UserError('No hay configuración activa de Leal API. Por favor, configure y autentique primero.')
        return config
    
    @api.model
    def get_token_for_frontend(self):
        """Método para obtener el token desde el frontend JavaScript"""
        try:
            config = self.get_active_config()
            
            if not config.is_token_valid():
                # Intentar obtener un token válido
                try:
                    config.get_valid_token()
                except Exception as e:
                    return {
                        'success': False,
                        'message': str(e),
                        'config_exists': True,
                        'is_authenticated': config.is_authenticated
                    }
            
            return {
                'success': True,
                'token': config.access_token,
                'expires_at': config.token_expires_at.isoformat() if config.token_expires_at else None,
                'username': config.username,
                'last_auth_date': config.last_auth_date.isoformat() if config.last_auth_date else None,
                'api_url': config.api_url
            }
        except Exception as e:
            return {
                'success': False,
                'message': str(e),
                'config_exists': False,
                'is_authenticated': False
            }
    
    def get_user_data(self):
        """Obtiene los datos del usuario asociados con esta configuración"""
        self.ensure_one()
        user_data = self.env['leal.user.data'].search([('api_settings_id', '=', self.id)], limit=1)
        return user_data
    
    def refresh_user_data(self):
        """Refresca los datos del usuario desde la API"""
        self.ensure_one()
        if not self.is_authenticated:
            raise UserError('La configuración no está autenticada.')
        
        api_client = self.env['leal.api.client']
        return api_client.get_user_data_after_auth(self.id)
    
    def action_view_user_data(self):
        """Abre la vista de los datos del usuario"""
        self.ensure_one()
        user_data = self.get_user_data()
        
        if not user_data:
            raise UserError('No hay datos de usuario guardados. Por favor, autentíquese primero.')
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Datos del Usuario Leal',
            'res_model': 'leal.user.data',
            'view_mode': 'form',
            'res_id': user_data.id,
            'target': 'current',
        }

    @api.model
    def search_customer(self, document_number):
        """Busca un cliente por su número de documento en la API de Leal"""
        _logger.info(f"[LEAL] Buscando cliente con documento: {document_number}")
        
        try:
            
            config = self.get_active_config()
            user = config.get_user_data() 
            
            token = config.get_valid_token()
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {token}'
            }
            
            search_url = f"{config.api_url}/usu_usuarios/buscar_usuario/{user.id_comercio}/{document_number}"
            
            _logger.info(f"[LEAL] Buscando cliente en: {search_url} con documento: {document_number}")
            
            response = requests.get(search_url,
                                   headers=headers, 
                                   timeout=30)
            
            response.raise_for_status()
            result = response.json()
            
            if result['code'] == 100:
                customers = result.get('data', [])

                return {
                    'success': True,
                    'message': 'Cliente encontrado exitosamente.',
                    'data': customers
                }
            else:
                error_message = result.get('message', 'Cliente no encontrado')
                _logger.warning(f"[LEAL] Cliente no encontrado: {error_message}")
                
                return {
                    'success': False,
                    'message': error_message,
                    'data': None
                }
                
        except requests.exceptions.RequestException as e:
            _logger.error(f"[LEAL] Error de conexión al buscar cliente: {str(e)}")
            return {
                'success': False,
                'message': f"Error de conexión: {str(e)}",
                'data': None
            }
        except Exception as e:
            _logger.error(f"[LEAL] Error al buscar cliente: {str(e)}")
            return {
                'success': False,
                'message': f"Error: {str(e)}",
                'data': None
            }

    @api.model
    def get_user_rewards(self, id_user):

        try:
            config = self.get_active_config()

            token = config.get_valid_token()
            if not token:
                raise UserError('No hay token de autenticación válido. Por favor, autentíquese primero.')
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {token}'
            }
                
            rewards_url = f"{config.api_url}/com_comercios/premios-homologados/{id_user}"
            
            _logger.info(f"Obteniendo recompensas para usuario ID: {id_user} en: {rewards_url}")
            
            response = requests.get(rewards_url, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if result['code'] == 100:
                productos = result['data']
                if not productos:
                    _logger.warning(f"No se encontraron recompensas para el usuario ID: {id_user}")
                    return {
                        'success': False,
                        'message': 'No se encontraron recompensas disponibles.',
                        'data': []
                    }
                return {
                    'success': True,
                    'data': result['data']
                }
            else:
                error_message = result.get('message', f'Error al obtener recompensas {result["code"]}')
                _logger.error(f"Error al obtener recompensas: {error_message}")
                return {
                    'success': False,
                    'message': error_message,
                    'data': None
                }
                
        except requests.exceptions.RequestException as e:
            _logger.error(f"Error de conexión al obtener recompensas: {str(e)}")
            return {
                'success': False,
                'message': f"Error de conexión: {str(e)}",
                'data': None
            }
        except Exception as e:
            _logger.error(f"Error al obtener recompensas: {str(e)}")
            return {
                'success': False,
                'message': f"Error: {str(e)}",
                'data': None
            }
            
    @api.model
    def send_otp_to_customer(self, data):
        """Envía un OTP al usuario especificado"""
        try:
            config = self.get_active_config()        
                
            token = config.get_valid_token()
            if not token:
                raise UserError('No hay token de autenticación válido. Por favor, autentíquese primero.')
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {token}'
            }
            
            otp_url = f"{config.api_url}/usu_historial_puntos/generarOTPRedencion"
            response = requests.post(otp_url, headers=headers, timeout=30, json=data)
            response.raise_for_status()
            result = response.json()
            
            _logger.info(f"[LEAL] Enviando OTP a cliente: {data}")
            return result
        except requests.exceptions.RequestException as e:
            _logger.error(f"[LEAL] Error de conexión al enviar el OTP: {str(e)}")
            return {
                'success': False,
                'message': f"Error de conexión: {str(e)}",
                'data': None
            }
        except Exception as e:
            _logger.error(f"[LEAL] Error al enviar el OTP: {str(e)}")
            return {
                'success': False,
                'message': f"Error: {str(e)}",
                'data': None
        
            }
    
    @api.model
    def redeem_points(self, data):
        """Redime puntos del usuario a través del API"""
        try:
            config = self.get_active_config()        
                
            token = config.get_valid_token()
            if not token:
                raise UserError('No hay token de autenticación válido. Por favor, autentíquese primero.')
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {token}'
            }
            
            redeem_url = f"{config.api_url}/usu_historial_puntos/redimir_puntos"
            
            _logger.info(f"Redimiendo puntos: {data}")
            
            response = requests.post(redeem_url, headers=headers, timeout=30, json=data)
            response.raise_for_status()
            result = response.json()
            
            return result
            
        except requests.exceptions.RequestException as e:
            _logger.error(f"Error de conexión al redimir puntos: {str(e)}")
            return {
                'code': 500,
                'message': f"Error de conexión: {str(e)}",
                'data': None
            }
        except Exception as e:
            _logger.error(f"Error al redimir puntos: {str(e)}")
            return {
                'code': 500,
                'message': f"Error: {str(e)}",
                'data': None
            }
            
    @api.model
    def refund_order(self, data):
        """Solicita un reembolso de una orden a través del API"""
        try:
            config = self.get_active_config()        
                
            token = config.get_valid_token()
            if not token:
                raise UserError('No hay token de autenticación válido. Por favor, autentíquese primero.')
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {token}'
            }
            
            refund_url = f"{config.api_url}/usu_balance_puntos/eliminar_transaccion"
            
            response = requests.post(refund_url, headers=headers, timeout=30, json=data)
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') != 100:
                error_message = result.get('message', 'Error al solicitar reembolso')
                _logger.error(f"Error al solicitar reembolso: {error_message}")
                return {
                    'code': result.get('code', 500),
                    'message': error_message,
                    'data': None
                }
            
            return result
            
        except requests.exceptions.RequestException as e:
            _logger.error(f"Error de conexión al solicitar reembolso: {str(e)}")
            return {
                'code': 500,
                'message': f"Error de conexión: {str(e)}",
                'data': None
            }
        except Exception as e:
            _logger.error(f"Error al solicitar reembolso: {str(e)}")
            return {
                'code': 500,
                'message': f"Error: {str(e)}",
                'data': None
            }
    
    @api.model
    def get_config_by_key(self, campo):
        """
        Obtiene el valor de la configuración 'redencion_abierta' del usuario actual
        Retorna True si redencion_abierta != 0, False si redencion_abierta = 0
        """
        try:
            config = self.get_active_config()
            user_data = config.get_user_data()
            
            if not user_data:
                _logger.warning("No hay datos de usuario para obtener configuración redencion_abierta")
                return None
            
            config_record = user_data.config_ids.filtered(lambda c: c.config_key == str(campo))
            
            if config_record:
                
                if config_record.config_value_int is not None:
                    return str(config_record.config_value_int)
                else:
                    return None
            
            _logger.warning(f"No se encontró la configuración '{campo}' en los datos del usuario")
            return None
            
        except Exception as e:
            _logger.error(f"Error al obtener configuración {campo}: {str(e)}")
            return None
    
    ## requridos para buscar campañas
    @api.model
    def search_costumer_campaigns(self, customer_uid):
        try:
            config = self.get_active_config()
            user = config.get_user_data() 
            token = config.get_valid_token('ct')
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {token}'
            }
            
            search_url = f"{config.api_url_ct}/crm/api/redemptions/v1/redemptions/get-campaign-redemption/{user.id_comercio}/{customer_uid}"
            
            response = requests.get(search_url, headers=headers, timeout=30)
            
            response.raise_for_status()
            result = response.json()
            
            return result
        except Exception as e:
            _logger.error(f"Error al buscar campañas para usuario {customer_uid}: {str(e)}")
            return e
        
    @api.model
    def leal_accumulation(self, data):
        """Solicita una acumulación de puntos a través del API"""
        try:
            config = self.get_active_config()
            user = config.get_user_data()
            token = config.get_valid_token()
            if not token:
                raise UserError('No hay token de autenticación válido. Por favor, autentíquese primero.')
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {token}'
            }
            
            accumulation_url = f"{config.api_url}/usu_historial_puntos/cargar_factura/{user.id_comercio}"
            response = requests.post(accumulation_url, headers=headers, timeout=30, json=data)
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') == 100:
                try:
                    pos_order = None
                    customer = None
                    
                    if 'transaccion' in data and 'noFactura' in data['transaccion']:
                        no_factura = data['transaccion']['noFactura']
                        pos_order = self.env['pos.order'].search([('name', 'ilike', no_factura.split()[0])], limit=1)
                    
                    if data.get('uid'):
                        leal_user_data = self.env['leal.user.data'].search([('uid_cms', '=', data['uid'])], limit=1)
                        if leal_user_data:
                            if leal_user_data.correo:
                                customer = self.env['res.partner'].search([('email', '=', leal_user_data.correo)], limit=1)
                            if not customer and leal_user_data.nombre:
                                customer = self.env['res.partner'].search([('name', 'ilike', leal_user_data.nombre)], limit=1)
                    
                    self.env['leal.accumulate.response'].create_from_api_response(
                        response_data=result,
                        pos_order=pos_order,
                        customer=customer
                    )
                    
                    _logger.info(f"Respuesta de acumulación guardada exitosamente: {result.get('id_transaccion')}")
                    
                except Exception as save_error:
                    _logger.error(f"Error al guardar la respuesta de acumulación: {str(save_error)}")
            else:
                error_message = result.get('message', 'Error al acumular puntos')
                _logger.error(f"Error al acumular puntos: {data}")
            
            return result
            
        except Exception as e:
            _logger.error(f"Error al acumular puntos: {str(e)}")
            return e
        
    @api.model
    def leal_campaign_redeem(self, data):
        """Solicita una redención de puntos a través del API para caso de uso campañas"""
        try:
            config = self.get_active_config()
            # user = config.get_user_data()
            token = config.get_valid_token('ct')
            if not token:
                raise UserError('No hay token de autenticación válido. Por favor, autentíquese primero.')
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {token}'
            }
            
            redeem_url = f"{config.api_url_ct}/crm/api/redemptions/v1/redemptions/redeem-campaign"
            response = requests.post(redeem_url, headers=headers, timeout=30, json=data)
            response.raise_for_status()
            result = response.json()
            
            if result.get('statusCode') == 200:
                return {
                    "status": "success",
                    "message" : "Redención exitosa",
                    "data": result,
                }
            else:
                return {
                    "status": "error",
                    "message" : result.get('message', 'Error al redenciar puntos'),
                    "data": result,
                }
                    
        except Exception as e:
            _logger.error(f"Error al redenciar puntos: {str(e)}")
            return {
                "status": "error",
                "message" : e,
            }