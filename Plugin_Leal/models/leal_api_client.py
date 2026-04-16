from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import requests
import json
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

class LealApiClient(models.Model):
    _name = 'leal.api.client'
    _description = 'Cliente API Leal'

    @api.model
    def get_user_data_after_auth(self, api_settings_id):
        """
        Obtiene los datos del usuario después de la autenticación exitosa
        """
        api_settings = self.env['leal.api.settings'].browse(api_settings_id)
        
        if not api_settings.exists():
            raise UserError('Configuración API no encontrada.')
        
        try:
            # Obtener token válido
            token = api_settings.get_valid_token()
            
            # Headers para la petición
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {token}'
            }
            
            # Hacer llamada al endpoint para obtener datos del usuario
            user_data_url = f"{api_settings.api_url}/com_usuarios/me"
            
            response = requests.get(user_data_url, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') == 100:
                # Procesar y guardar los datos
                self._process_and_save_user_data(result, api_settings)
                
                return {
                    'success': True,
                    'message': 'Datos del usuario obtenidos y guardados exitosamente.',
                    'data': result
                }
            else:
                error_message = result.get('message', 'Error desconocido al obtener datos del usuario')
                raise UserError(f"Error en la API: {error_message}")
                
        except requests.exceptions.RequestException as e:
            _logger.error(f"Error de conexión al obtener datos del usuario: {str(e)}")
            raise UserError(f"Error de conexión: {str(e)}")
        except Exception as e:
            _logger.error(f"Error al obtener datos del usuario: {str(e)}")
            raise UserError(f"Error: {str(e)}")
    
    def _process_and_save_user_data(self, api_response, api_settings):
        """
        Procesa la respuesta de la API y guarda los datos en los modelos correspondientes
        """
        user_data = api_response.get('data', {})
        user_info = api_response.get('user', {})
        
        # Combinar datos de 'user' y 'data' (parecen ser duplicados en el JSON)
        combined_data = {**user_info, **user_data}
        
        # Preparar valores para el modelo leal.user.data
        user_vals = {
            'uid_cms': combined_data.get('uid_cms'),
            'username': combined_data.get('username'),
            'nombre': combined_data.get('nombre'),
            'correo': combined_data.get('correo'),
            'id_comercio': combined_data.get('id_comercio'),
            'nombre_comercio': combined_data.get('nombre_comercio'),
            'nombre_corto': combined_data.get('nombre_corto'),
            'id_sucursal': combined_data.get('id_sucursal'),
            'imagen_comercio': combined_data.get('imagen_comercio'),
            'tipo_comercio': combined_data.get('tipo_comercio'),
            'id_rol': combined_data.get('id_rol'),
            'rol_name': combined_data.get('rol_name'),
            'rol': combined_data.get('rol'),
            'id_franquicia': combined_data.get('id_franquicia'),
            'id_plan': combined_data.get('id_plan'),
            'miles_cop1': combined_data.get('miles_cop1'),
            'puntos_termometro': combined_data.get('puntos_termometro'),
            'cod_moneda': combined_data.get('cod_moneda'),
            'cod_pais': combined_data.get('cod_pais'),
            'tiene_pin': bool(combined_data.get('tiene_pin', 0)),
            'tiene_otp': bool(combined_data.get('tiene_otp', 0)),
            'iat': combined_data.get('iat'),
            'exp': combined_data.get('exp'),
            'tipo_lc': combined_data.get('tipoLC'),
            'marca_blanca': bool(combined_data.get('marcaBlanca', False)),
            'api_settings_id': api_settings.id,
            'fecha_obtencion': fields.Datetime.now(),
            'activo': True
        }
        
        user_data_record = self.env['leal.user.data'].create(user_vals)
        
        config_data = combined_data.get('config', {})
        if config_data:
            self._save_user_configurations(user_data_record, config_data)
        
        _logger.info(f"Datos del usuario {user_vals['username']} guardados exitosamente.")
        
        return user_data_record
    
    def _save_user_configurations(self, user_data_record, config_data):
        # Mapeo de configuraciones con descripciones
        config_descriptions = {
            'compartir_fb': 'Configuración para compartir en Facebook',
            'vencimiento_puntos': 'Meses para vencimiento de puntos',
            'valor_por_punto_redencion': 'Valor por punto en redención',
            'limite': 'Límite de transacciones',
            'factura_obligatoria': 'Factura obligatoria',
            'registro_rapido_primero': 'Registro rápido primero',
            'texaco': 'Configuración Texaco',
            'solo_premios_posibles': 'Solo premios posibles',
            'bloquear_perfiles_incompletos': 'Bloquear perfiles incompletos',
            'bloquear_acceso_web': 'Bloquear acceso web',
            'recibir_detalles_factura': 'Recibir detalles de factura',
            'bloquear_historial': 'Bloquear historial',
            'ocultar_logout': 'Ocultar logout',
            'ocultar_redencion': 'Ocultar redención',
            'email_opcional': 'Email opcional',
            'imprime_recibo': 'Imprime recibo',
            'cedula_editable': 'Cédula editable',
            'redencion_abierta': 'Redención abierta',
            'banderazo_promocion': 'Banderazo promoción',
            'bloquear_popup_factura': 'Bloquear popup factura',
            'agregar_usuario_manual': 'Agregar usuario manual',
            'ocultar_registro': 'Ocultar registro',
            'ocultar_genero_otro': 'Ocultar género otro',
            'ocultar_acumulacion': 'Ocultar acumulación',
            'usuarios_empresa': 'Usuarios empresa',
            'cargar_pts_pago_lc': 'Cargar puntos pago LC',
            'descuento_moneda': 'Descuento moneda'
        }
        
        # Eliminar configuraciones existentes para este usuario
        existing_configs = self.env['leal.user.config'].search([('user_data_id', '=', user_data_record.id)])
        existing_configs.unlink()
        
        # Crear nuevas configuraciones
        for key, value in config_data.items():
            config_vals = {
                'user_data_id': user_data_record.id,
                'config_key': key,
                'descripcion': config_descriptions.get(key, f'Configuración {key}')
            }
            
            # Determinar el tipo de valor y asignarlo al campo correspondiente
            if isinstance(value, bool):
                config_vals['config_value_bool'] = value
            elif isinstance(value, int):
                config_vals['config_value_int'] = value
            else:
                config_vals['config_value'] = str(value)
            
            self.env['leal.user.config'].create(config_vals)
        
        _logger.info(f"Guardadas {len(config_data)} configuraciones para usuario {user_data_record.username}")
    
    @api.model
    def refresh_user_data(self, api_settings_id=None):
        """
        Refresca los datos del usuario desde la API
        """
        if not api_settings_id:
            # Obtener la configuración activa
            api_settings = self.env['leal.api.settings'].search([('active', '=', True)], limit=1)
            if not api_settings:
                raise UserError('No hay configuración API activa.')
            api_settings_id = api_settings.id
        
        return self.get_user_data_after_auth(api_settings_id)
    
    @api.model
    def get_current_user_data(self):
        """
        Obtiene los datos del usuario actual desde la base de datos
        """
        api_settings = self.env['leal.api.settings'].search([('active', '=', True)], limit=1)
        if not api_settings:
            raise UserError('No hay configuración API activa.')
        
        user_data = self.env['leal.user.data'].search([('api_settings_id', '=', api_settings.id)], limit=1)
        if not user_data:
            raise UserError('No hay datos de usuario guardados. Por favor, autentíquese primero.')
        
        return {
            'user_data': user_data,
            'configurations': user_data.config_ids
        }
    
    @api.model
    def cleanup_old_user_data(self, days_old=30):
        """
        Limpia datos de usuario antiguos (por defecto más de 30 días)
        """
        from datetime import datetime, timedelta
        
        cutoff_date = fields.Datetime.now() - timedelta(days=days_old)
        old_data = self.env['leal.user.data'].search([
            ('fecha_obtencion', '<', cutoff_date),
            ('activo', '=', False)
        ])
        
        if old_data:
            count = len(old_data)
            old_data.unlink()
            _logger.info(f"Eliminados {count} registros antiguos de datos de usuario.")
            return count
        
        return 0
