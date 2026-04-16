from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class LealUserData(models.Model):
    _name = 'leal.user.data'
    _description = 'Datos del Usuario Leal'
    _rec_name = 'username'

    # Campos principales del usuario
    uid_cms = fields.Char(string='UID CMS', readonly=True)
    username = fields.Char(string='Nombre de Usuario', readonly=True)
    nombre = fields.Char(string='Nombre', readonly=True)
    correo = fields.Char(string='Correo', readonly=True)
    
    # Campos del comercio
    id_comercio = fields.Integer(string='ID Comercio', readonly=True)
    nombre_comercio = fields.Char(string='Nombre Comercio', readonly=True)
    nombre_corto = fields.Char(string='Nombre Corto', readonly=True)
    id_sucursal = fields.Char(string='ID Sucursal', readonly=True)
    imagen_comercio = fields.Char(string='Imagen Comercio', readonly=True)
    tipo_comercio = fields.Char(string='Tipo Comercio', readonly=True)
    
    # Campos de rol y permisos
    id_rol = fields.Integer(string='ID Rol', readonly=True)
    rol_name = fields.Char(string='Nombre Rol', readonly=True)
    rol = fields.Char(string='Rol', readonly=True)
    id_franquicia = fields.Integer(string='ID Franquicia', readonly=True)
    id_plan = fields.Integer(string='ID Plan', readonly=True)
    
    # Campos monetarios y puntos
    miles_cop1 = fields.Integer(string='Miles COP', readonly=True)
    puntos_termometro = fields.Integer(string='Puntos Termómetro', readonly=True)
    cod_moneda = fields.Char(string='Código Moneda', readonly=True)
    cod_pais = fields.Char(string='Código País', readonly=True)
    
    # Campos de seguridad
    tiene_pin = fields.Boolean(string='Tiene PIN', readonly=True)
    tiene_otp = fields.Boolean(string='Tiene OTP', readonly=True)
    
    # Campos de token JWT
    iat = fields.Integer(string='Token Emitido', readonly=True, help='Timestamp de cuando fue emitido el token')
    exp = fields.Integer(string='Token Expira', readonly=True, help='Timestamp de cuando expira el token')
    
    # Campos especiales
    tipo_lc = fields.Char(string='Tipo LC', readonly=True)
    marca_blanca = fields.Boolean(string='Marca Blanca', readonly=True)
    
    # Relación con la configuración
    api_settings_id = fields.Many2one('leal.api.settings', string='Configuración API', required=True, ondelete='cascade')
    
    # Campos de control
    fecha_obtencion = fields.Datetime(string='Fecha Obtención', default=fields.Datetime.now, readonly=True)
    activo = fields.Boolean(string='Activo', default=True)
    
    # Relación con configuraciones del comercio
    config_ids = fields.One2many('leal.user.config', 'user_data_id', string='Configuraciones')
    
    @api.model_create_multi
    def create(self, vals_list):
        # Convertir vals a lista si no lo es (para compatibilidad)
        if not isinstance(vals_list, list):
            vals_list = [vals_list]
        
        records_to_create = []
        existing_records = self.browse()
        
        for vals in vals_list:
            # Verificar que no exista ya un registro para esta configuración
            existing = self.search([('api_settings_id', '=', vals.get('api_settings_id'))], limit=1)
            if existing:
                # Actualizar el registro existente en lugar de crear uno nuevo
                existing.write(vals)
                existing_records |= existing
            else:
                records_to_create.append(vals)
        
        # Crear solo los registros que no existen
        new_records = self.browse()
        if records_to_create:
            new_records = super().create(records_to_create)
        
        return existing_records | new_records
    
    def refresh_user_data(self):
        """Refresca los datos del usuario desde la API"""
        self.ensure_one()
        
        api_client = self.env['leal.api.client']
        try:
            result = api_client.refresh_user_data(self.api_settings_id.id)
            if result.get('success'):
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Datos Actualizados',
                        'message': 'Los datos del usuario han sido actualizados exitosamente.',
                        'type': 'success',
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Error',
                        'message': result.get('message', 'Error desconocido'),
                        'type': 'danger',
                    }
                }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': str(e),
                    'type': 'danger',
                }
            }

class LealUserConfig(models.Model):
    _name = 'leal.user.config'
    _description = 'Configuraciones del Usuario Leal'
    _rec_name = 'config_key'

    user_data_id = fields.Many2one('leal.user.data', string='Usuario Leal', required=True, ondelete='cascade')
    config_key = fields.Char(string='Clave Configuración', required=True)
    config_value = fields.Char(string='Valor Configuración')
    config_value_int = fields.Integer(string='Valor Entero')
    config_value_bool = fields.Boolean(string='Valor Booleano')
    descripcion = fields.Char(string='Descripción')
    
    _sql_constraints = [
        ('unique_config_per_user', 'unique(user_data_id, config_key)', 'No puede haber configuraciones duplicadas para el mismo usuario.')
    ]
