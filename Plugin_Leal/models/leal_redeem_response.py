# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json
import logging

_logger = logging.getLogger(__name__)

class LealRedeemResponse(models.Model):
    _name = 'leal.redeem.response'
    _description = 'Respuestas de Redención Leal'
    _order = 'create_date desc'
    _rec_name = 'no_factura'

    code = fields.Integer(string='Código de Respuesta', required=True)
    no_factura = fields.Char(string='Número de Factura')
    id_transaccion = fields.Char(string='ID Transacción')
    puntos_activos = fields.Integer(string='Puntos Activos')
    puntos = fields.Integer(string='Puntos')
    message = fields.Text(string='Mensaje')
    
    uid_customer = fields.Char(string='UID Cliente')
    id_premio = fields.Char(string='ID Premio')
    codigo_premio = fields.Char(string='Código Premio')
    valor_redencion = fields.Float(string='Valor de Redención')
    id_comercio = fields.Integer(string='ID Comercio')
    id_sucursal = fields.Char(string='ID Sucursal')
    
    odoo_ticket_code = fields.Char(string='Odoo Ticket Code')
    odoo_product_id = fields.Many2one('product.product', string='Producto Odoo')
    
    response_json = fields.Text(string='Respuesta JSON Completa')
    
    create_date = fields.Datetime(string='Fecha de Creación', default=fields.Datetime.now, readonly=True)
    create_uid = fields.Many2one('res.users', string='Creado por', readonly=True, default=lambda self: self.env.user)
    
    state = fields.Selection([
        ('success', 'Exitoso'),
        ('error', 'Error'),
        ('invalid_otp', 'OTP Inválido'),
        ('other', 'Otro')
    ], string='Estado', compute='_compute_state', store=True)
    
    @api.depends('code')
    def _compute_state(self):
        """Calcula el estado basado en el código de respuesta"""
        for record in self:
            if record.code == 100:
                record.state = 'success'
            elif record.code == 109:
                record.state = 'invalid_otp'
            else:
                record.state = 'error' if record.code != 100 else 'other'
    
    @api.model
    def create_from_response(self, response_data, context_data=None):
        try:
            if context_data is None:
                context_data = {}
            
            vals = {
                'code': response_data.get('code', 0),
                'no_factura': response_data.get('no_factura', ''),
                'id_transaccion': str(response_data.get('id_transaccion', '')),
                'puntos_activos': response_data.get('puntos_activos', 0),
                'puntos': response_data.get('puntos', 0),
                'message': response_data.get('message', ''),
                'response_json': json.dumps(response_data, ensure_ascii=False, indent=2),
            }
            
            if context_data:
                vals.update({
                    'uid_customer': context_data.get('uid_customer', ''),
                    'id_premio': context_data.get('id_premio', ''),
                    'codigo_premio': context_data.get('codigo_premio', ''),
                    'valor_redencion': context_data.get('valor_redencion', 0.0),
                    'id_comercio': context_data.get('id_comercio', 0),
                    'id_sucursal': context_data.get('id_sucursal', ''),
                    'odoo_ticket_code': context_data.get('odoo_ticket_code', None),
                    'odoo_product_id': context_data.get('odoo_product_id', None),
                    'no_factura': context_data.get('no_factura', ''),
                })
            
            record = self.create(vals)
            _logger.info(f"LEAL - Registro de redención creado exitosamente: ID {record.id}, Código {vals['code']}")
            return record
            
        except Exception as e:
            _logger.error(f"LEAL - Error al crear registro de redención: {e}")
            pass
    
    def name_get(self):
        """Personaliza el nombre mostrado en el registro"""
        result = []
        for record in self:
            if record.no_factura:
                name = f"{record.no_factura} ({record.code})"
            else:
                name = f"Código {record.code} - {record.create_date.strftime('%Y-%m-%d %H:%M')}"
            result.append((record.id, name))
        return result

    @api.model
    def find_order_by_partial_invoice(self, partial_invoice_number):
        if not partial_invoice_number:
            return []
        domain = [
            ('odoo_ticket_code', 'ilike', f'%{partial_invoice_number}%'),
            ('state', '=', 'success')
        ]
        orders = self.search(domain)
        return orders.read()
    
    @api.model
    def get_order_from_orderline_id(self, orderline_id):
        if not orderline_id:
            _logger.warning("ID de línea de orden no proporcionado")
            return []
        try:
            # El ID puede venir como string desde JS
            orderline = self.env['pos.order.line'].browse(int(orderline_id))
            
            if not orderline.exists():
                _logger.warning(f"No se encontró línea de orden con ID: {orderline_id}")
                return []
            
            order = orderline.order_id
            if not order:
                _logger.warning(f"La línea de orden {orderline_id} no tiene una orden asociada.")
                return []

            payment_data = []
            for payment in order.payment_ids:
                payment_method = payment.payment_method_id
                if payment_method:
                    payment_data.append({
                        'id': payment_method.id,
                        'name': payment_method.name,
                        'amount': payment.amount,
                        'payment_date': payment.payment_date.strftime('%Y-%m-%d %H:%M:%S') if payment.payment_date else None,
                    })
            
            _logger.info(f"Métodos de pago encontrados para la orden {order.name}: {payment_data}")
            return payment_data
            
        except Exception as e:
            _logger.error(f"Error al buscar métodos de pago por línea de orden ID {orderline_id}: {e}")
            return []
    
    @api.model
    def get_ticket_code_from_orderline_id(self, orderline_id):
        """
        Obtiene el nombre/número de una orden POS buscando en pos.order.line por el ID de la línea.
        
        Args:
            orderline_id (int): ID de la línea de orden (pos.order.line)
            
        Returns:
            str or False: Nombre de la orden (pos.order.name) si se encuentra, False en caso contrario
        """
        if not orderline_id:
            _logger.warning("ID de línea de orden no proporcionado")
            return False
            
        try:
            # Buscar la línea de orden en pos.order.line
            orderline = self.env['pos.order.line'].browse(orderline_id)
            
            if not orderline.exists():
                _logger.warning(f"No se encontró línea de orden con ID: {orderline_id}")
                return False
            
            # Obtener el nombre de la orden padre
            ticket_code = orderline.order_id.ticket_code if orderline.order_id else False
            
            if ticket_code:
                _logger.info(f"Orden encontrada: {ticket_code} (ID: {orderline.order_id.id}) para línea {orderline_id}")
            else:
                _logger.warning(f"La línea {orderline_id} no tiene orden asociada")
                
            return ticket_code
            
        except Exception as e:
            _logger.error(f"Error al buscar nombre de orden por línea ID {orderline_id}: {e}")
            return False

