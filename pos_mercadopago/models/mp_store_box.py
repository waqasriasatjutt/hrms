# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import requests
import logging
_logger = logging.getLogger(__name__)


class MPStoreBoxLine(models.Model):
    _name = 'mp.store.box.line'
    _description = "Pos Terminal mp"

    config_id = fields.Many2one('pos.config', string="Punto de venta")
    name = fields.Char(string="Nombre de la caja", related='config_id.name', store=True)
    category = fields.Selection(
        [
            ('621102', 'Argentina')
        ],
        string='Código MCC', default='621102')
    external_id = fields.Char(string="Identificador único de la caja")
    store_box_id = fields.Many2one('mp.store.box', string="Sucursal física", ondelete='cascade')
    fixed_amount = fields.Boolean(string="Fixed amount")
    box_id = fields.Char(string="Box ID")
    store_id = fields.Char(string="Store")
    external_store_id = fields.Char(string="External Store")
    user_id = fields.Char(string="User")
    active_box = fields.Boolean(string="Estado")

    def remove_point_box(self):
        """Elimina un punto de venta de MercadoPago"""
        if not self.box_id:
            self.unlink()
            return

        credential_id = self.store_box_id.pos_mp_config_id
        if not credential_id or not credential_id.mp_access_token:
            raise ValidationError('Credenciales de MercadoPago no configuradas correctamente')

        url = f"{credential_id.mp_url}/pos/{self.box_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {credential_id.mp_access_token}",
        }

        try:
            response = requests.delete(url, headers=headers, timeout=30)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as error:
            raise ValidationError(f'Error de conexión con MercadoPago: {error}')
        except requests.exceptions.RequestException as error:
            raise ValidationError(f'Error en la petición: {error}')

        if response.status_code == 204:
            self.unlink()
        else:
            try:
                data_to_json = response.json()
                error_msg = data_to_json.get('message', data_to_json.get('error', str(data_to_json)))
            except ValueError:
                error_msg = f'Error HTTP {response.status_code}'
            raise ValidationError(f'Error MercadoPago: {error_msg}')

    def edit_point_box(self):
        """Edita un punto de venta en MercadoPago"""
        if not self.box_id:
            raise ValidationError('El punto de venta no tiene ID para editar')

        credential_id = self.store_box_id.pos_mp_config_id
        if not credential_id or not credential_id.mp_access_token:
            raise ValidationError('Credenciales de MercadoPago no configuradas correctamente')

        url = f"{credential_id.mp_url}/pos/{self.box_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {credential_id.mp_access_token}",
        }

        payload = {
            "category": int(self.category),
            "fixed_amount": self.fixed_amount,
            "name": self.name,
            "store_id": int(self.store_box_id.store_id.external_store_id)
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
            qr_data = data_to_json.get('qr', {})
            if not qr_data or not data_to_json.get('id'):
                raise ValidationError('Respuesta incompleta de MercadoPago')

            self.write({
                'image_qr': qr_data.get('image'),
                'template_document_qr': qr_data.get('template_document'),
                'template_image_qr': qr_data.get('template_image'),
                'qr_code': data_to_json.get('qr_code'),
                'box_id': data_to_json['id'],
                'active_box': True
            })
            # Mostrar notificación de éxito
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Actualización exitosa',
                    'message': 'El punto de venta ha sido actualizado correctamente.',
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            error_msg = data_to_json.get('message', data_to_json.get('error', str(data_to_json)))
            raise ValidationError(f'Error MercadoPago: {error_msg}')


class MPStoreBox(models.Model):
    _name = 'mp.store.box'
    _description = 'Mp Store Box'
    _rec_name = 'store_id'

    name = fields.Char(string="Punto de venta ID")
    store_id = fields.Many2one('mp.store', string="Sucursal física")
    pos_mp_config_id = fields.Many2one('mp.credential', string='Credencial', related='store_id.pos_mp_config_id')
    external_store_id = fields.Char(string="Identificador del la Sucursales físicas", related='store_id.external_store_id')
    box_line_ids = fields.One2many(
        "mp.store.box.line",
        "store_box_id",
        string="Terminal Line"
    )
    state = fields.Selection(
        [
            ('draft', 'Borrador'),
            ('publish', 'Publicado')
        ],
        string='Estado', default='draft'
    )

    def publish_box(self):
        """Publica puntos de venta en MercadoPago"""
        credential_id = self.pos_mp_config_id
        if not credential_id or not credential_id.mp_access_token:
            raise ValidationError('Credenciales de MercadoPago no configuradas correctamente')

        url = f"{credential_id.mp_url}/pos"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {credential_id.mp_access_token}",
        }

        for rec in self:
            inactive_boxes = rec.box_line_ids.filtered(lambda x: not x.active_box)

            for box in inactive_boxes:
                payload = {
                    "category": int(box.category),
                    "external_id": f"{rec.store_id.external_id}POS{box.config_id.id}{box.id}",
                    "external_store_id": rec.store_id.external_id,
                    "fixed_amount": box.fixed_amount,
                    "name": box.name,
                    "store_id": int(rec.store_id.external_store_id)
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
                    qr_data = data_to_json.get('qr', {})
                    if not qr_data or not data_to_json.get('id'):
                        raise ValidationError('Respuesta incompleta de MercadoPago')

                    box.write({
                        'image_qr': qr_data.get('image'),
                        'template_document_qr': qr_data.get('template_document'),
                        'template_image_qr': qr_data.get('template_image'),
                        'qr_code': data_to_json.get('qr_code'),
                        'box_id': data_to_json['id'],
                        'active_box': True,
                        'external_id': data_to_json.get('external_id'),
                        'store_id': data_to_json.get('store_id'),
                        'user_id': data_to_json.get('user_id'),
                        'external_store_id': data_to_json.get('external_store_id')
                    })
                else:
                    error_msg = data_to_json.get('message', data_to_json.get('error', str(data_to_json)))
                    raise ValidationError(f'Error MercadoPago: {error_msg}')

            # Verificar si todas las cajas están activas
            if rec.box_line_ids and all(box.active_box for box in rec.box_line_ids):
                rec.write({'state': 'publish'})

    def to_draft(self):
        for rec in self:
            rec.write({'state': 'draft'})
    
    def unlink(self):
        """
        Override unlink to check POS session state before deletion
        """
        for record in self:
            # Check if any box_line has an associated pos.config with non-closed session
            for box_line in record.box_line_ids:
                if box_line.config_id:
                    # Find the current active session for this pos.config
                    active_session = self.env['pos.session'].search([
                        ('config_id', '=', box_line.config_id.id),
                        ('state', '!=', 'closed')
                    ], limit=1)
                    
                    if active_session:
                        raise UserError(
                            f"No se puede eliminar el Store Box '{record.name}' porque el punto de venta "
                            f"'{box_line.config_id.name}' tiene una sesión activa (Estado: {active_session.state}). "
                            f"Debe cerrar la sesión antes de eliminar."
                        )
        
        # If all sessions are closed, proceed with deletion
        # Then delete the store_box records
        return super(MPStoreBox, self).unlink()