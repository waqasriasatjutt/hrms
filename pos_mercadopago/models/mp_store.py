# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import requests
import logging

_logger = logging.getLogger(__name__)

WEEKDAY_SELECTION = [
    ('MON', 'Lun'),
    ('TUE', 'Mar'),
    ('WED', 'Mié'),
    ('THU', 'Jue'),
    ('FRI', 'Vie'),
    ('SAT', 'Sáb'),
    ('SUN', 'Dom'),
]

RRULE_TYPE_SELECTION = [
    ('daily', 'Days'),
    ('weekly', 'Weeks'),
    ('monthly', 'Months'),
    ('yearly', 'Years'),
]

def _get_select_time(self):
    select_list_time = [('01:00', '01:00'), ('01:30', '01:30'), ('02:00', '02:00'), ('02:30', '02:30'),
                        ('03:00', '03:00'), ('03:30', '03:30'), ('04:00', '04:00'), ('04:30', '04:30'),
                        ('05:00', '05:00'), ('05:30', '05:30'), ('06:00', '06:00'), ('06:30', '06:30'),
                        ('07:00', '07:00'), ('07:30', '07:30'), ('08:00', '08:00'), ('08:30', '08:30'),
                        ('09:00', '09:00'), ('09:30', '09:30'), ('10:00', '10:00'), ('10:30', '10:30'),
                        ('11:00', '11:00'), ('11:30', '11:30'), ('12:00', '12:00'), ('12:30', '12:30'),
                        ('13:00', '13:00'), ('13:30', '13:30'), ('14:00', '14:00'), ('14:30', '14:30'),
                        ('15:00', '15:00'), ('15:30', '15:30'), ('16:00', '16:00'), ('16:30', '16:30'),
                        ('17:00', '17:00'), ('17:30', '17:30'), ('18:00', '18:00'), ('18:30', '18:30'),
                        ('19:00', '19:00'), ('19:30', '19:30'), ('20:00', '20:00'), ('20:30', '20:30'),
                        ('21:00', '21:00'), ('21:30', '21:30'), ('22:00', '22:00'), ('22:30', '22:30'),
                        ('23:00', '23:00'), ('23:30', '23:30'), ('23:59', '23:59'), ('00:00', '00:00'), ('00:30', '00:30'),
                        ]
    return select_list_time


def _get_select_time_close(self):
    select_list_time = [('01:00', '01:00'), ('01:30', '01:30'), ('02:00', '02:00'), ('02:30', '02:30'),
                        ('03:00', '03:00'), ('03:30', '03:30'), ('04:00', '04:00'), ('04:30', '04:30'),
                        ('05:00', '05:00'), ('05:30', '05:30'), ('06:00', '06:00'), ('06:30', '06:30'),
                        ('07:00', '07:00'), ('07:30', '07:30'), ('08:00', '08:00'), ('08:30', '08:30'),
                        ('09:00', '09:00'), ('09:30', '09:30'), ('10:00', '10:00'), ('10:30', '10:30'),
                        ('11:00', '11:00'), ('11:30', '11:30'), ('12:00', '12:00'), ('12:30', '12:30'),
                        ('13:00', '13:00'), ('13:30', '13:30'), ('14:00', '14:00'), ('14:30', '14:30'),
                        ('15:00', '15:00'), ('15:30', '15:30'), ('16:00', '16:00'), ('16:30', '16:30'),
                        ('17:00', '17:00'), ('17:30', '17:30'), ('18:00', '18:00'), ('18:30', '18:30'),
                        ('19:00', '19:00'), ('19:30', '19:30'), ('20:00', '20:00'), ('20:30', '20:30'),
                        ('21:00', '21:00'), ('21:30', '21:30'), ('22:00', '22:00'), ('22:30', '22:30'),
                        ('23:00', '23:00'), ('23:30', '23:30'), ('23:59', '23:59'), ('00:00', '00:00'), ('00:30', '00:30'),
                        ]
    return select_list_time


class MpStore(models.Model):
    _name = 'mp.store'
    _description = 'MP Store'

    name = fields.Char(string="Sucursal física")
    external_id = fields.Char(string="Identificador Sucursal física", store=True)
    street_number = fields.Char(string="Número de calle")
    street_name = fields.Char(string="Nombre de calle")
    city_name = fields.Char(string="Ciudad")
    state_id = fields.Many2one('res.country.state', string="Provincia")
    latitude = fields.Float('Geo Latitude', digits=(10, 7))
    longitude = fields.Float('Geo Longitude', digits=(10, 7))
    ref = fields.Char(string="Referencia")
    external_store_id = fields.Char(string="Store ID")
    address_id = fields.Char(string="Address ID")
    pos_mp_config_id = fields.Many2one('mp.credential', string='Credencial')

    mon = fields.Boolean(string='Lunes')
    tue = fields.Boolean()
    wed = fields.Boolean()
    thu = fields.Boolean()
    fri = fields.Boolean()
    sat = fields.Boolean()
    sun = fields.Boolean()
    weekday = fields.Selection(WEEKDAY_SELECTION, string='Weekday')
    interval = fields.Integer(default=1)
    rrule_type = fields.Selection(RRULE_TYPE_SELECTION, default='weekly')
    active_range = fields.Boolean(string='Active Range', default=False)
    h24 = fields.Boolean(string='24H', default=False)
    state = fields.Selection(
        [
            ('draft', 'Borrador'),
            ('publish', 'Publicado')
        ],
        string='Estado', default='draft'
    )

    # Monday
    open_time_mon = fields.Selection(selection=_get_select_time, string='Abre', store=True)
    close_time_mon = fields.Selection(selection=_get_select_time_close, string='Cierra', store=True)

    # Tuesday
    open_time_tue = fields.Selection(selection=_get_select_time, store=True)
    close_time_tue = fields.Selection(selection=_get_select_time_close, store=True)

    # Wednesday
    open_time_wed = fields.Selection(selection=_get_select_time, store=True)
    close_time_wed = fields.Selection(selection=_get_select_time_close, store=True)

    # Thursday
    open_time_thu = fields.Selection(selection=_get_select_time, store=True)
    close_time_thu = fields.Selection(selection=_get_select_time_close, store=True)

    # Friday
    open_time_fir = fields.Selection(selection=_get_select_time, store=True)
    close_time_fir = fields.Selection(selection=_get_select_time_close, store=True)

    # Saturday
    open_time_sat = fields.Selection(selection=_get_select_time, store=True)
    close_time_sat = fields.Selection(selection=_get_select_time_close, store=True)

    # Sunday
    open_time_sun = fields.Selection(selection=_get_select_time, store=True)
    close_time_sun = fields.Selection(selection=_get_select_time_close, store=True)

    def get_business_hours(self):
        """Obtiene los horarios de negocio para cada día de la semana"""
        days_mapping = {
            'monday': ('mon', 'open_time_mon', 'close_time_mon'),
            'tuesday': ('tue', 'open_time_tue', 'close_time_tue'),
            'wednesday': ('wed', 'open_time_wed', 'close_time_wed'),
            'thursday': ('thu', 'open_time_thu', 'close_time_thu'),
            'friday': ('fri', 'open_time_fir', 'close_time_fir'),
            'saturday': ('sat', 'open_time_sat', 'close_time_sat'),
            'sunday': ('sun', 'open_time_sun', 'close_time_sun'),
        }

        business_hours = {}
        for day_name, (active_field, open_field, close_field) in days_mapping.items():
            if getattr(self, active_field, False):
                business_hours[day_name] = [{
                    "open": getattr(self, open_field),
                    "close": getattr(self, close_field)
                }]

        return business_hours

    def publish_branch(self):
        """Publica una sucursal en MercadoPago"""
        credential_id = self.pos_mp_config_id
        if not credential_id or not credential_id.user_id or not credential_id.mp_access_token:
            raise ValidationError('Credenciales de MercadoPago no configuradas correctamente')

        url = f"{credential_id.mp_url}/users/{credential_id.user_id}/stores"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {credential_id.mp_access_token}",
        }
        payload = {
            "business_hours": self.get_business_hours(),
            "external_id": self.external_id,
            "location": {
                "street_number": self.street_number,
                "street_name": self.street_name,
                "city_name": self.city_name,
                "state_name": self.state_id.name,
                "latitude": self.latitude,
                "longitude": self.longitude,
                "reference": self.ref
            },
            "name": self.name
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as error:
            raise ValidationError(f'Error de conexión con MercadoPago: {error}')
        except requests.exceptions.RequestException as error:
            raise ValidationError(f'Error en la petición: {error}')

        try:
            data_to_json = response.json()
        except ValueError:
            raise ValidationError('Respuesta inválida de MercadoPago')

        if response.status_code == 201:
            if not data_to_json.get('id'):
                raise ValidationError('Respuesta incompleta de MercadoPago')
            self.write({
                'state': 'publish',
                'external_store_id': data_to_json['id'],
            })
        else:
            error_msg = data_to_json.get('message', 'Error desconocido')
            causes = data_to_json.get('causes', [])
            if causes:
                causas_detalle = "; ".join([c.get('description', '') for c in causes])
                error_msg = f"{error_msg} - Causas: {causas_detalle}"
            raise ValidationError(f'Error MercadoPago: {error_msg}')

    def update_branch(self):
        """Actualiza una sucursal en MercadoPago"""
        credential_id = self.pos_mp_config_id
        if not credential_id or not credential_id.user_id or not credential_id.mp_access_token:
            raise ValidationError('Credenciales de MercadoPago no configuradas correctamente')

        if not self.external_store_id:
            raise ValidationError('La sucursal no tiene ID externo para actualizar')

        url = f"{credential_id.mp_url}/users/{credential_id.user_id}/stores/{self.external_store_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {credential_id.mp_access_token}",
        }
        payload = {
            "business_hours": self.get_business_hours(),
            "external_id": self.external_id,
            "location": {
                "street_number": self.street_number,
                "street_name": self.street_name,
                "city_name": self.city_name,
                "state_name": self.state_id.name,
                "latitude": self.latitude,
                "longitude": self.longitude,
            },
            "name": self.name
        }
        try:
            response = requests.put(url, headers=headers, json=payload, timeout=30)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as error:
            raise ValidationError(f'Error de conexión con MercadoPago: {error}')
        except requests.exceptions.RequestException as error:
            raise ValidationError(f'Error en la petición: {error}')

        try:
            data_to_json = response.json()
        except ValueError:
            raise ValidationError('Respuesta inválida de MercadoPago')

        if response.status_code == 200:
            if not data_to_json.get('id') or not data_to_json.get('location', {}).get('id'):
                raise ValidationError('Respuesta incompleta de MercadoPago')
            self.write({
                'state': 'publish',
                'external_store_id': data_to_json['id'],
            })
        else:
            error_msg = data_to_json.get('message', data_to_json.get('error', str(data_to_json)))
            raise ValidationError(f'Error MercadoPago: {error_msg}')
