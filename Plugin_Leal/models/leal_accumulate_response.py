# -*- coding: utf-8 -*-

from odoo import models, fields, api


class LealAccumulateResponse(models.Model):
    _name = 'leal.accumulate.response'
    _description = 'Leal Accumulate Response'
    _order = 'create_date desc'

    # Campos de la respuesta del API
    code = fields.Integer(string='Code', required=True, help='Código de respuesta del API')
    id_transaccion = fields.Char(string='ID Transacción', required=True, help='ID de la transacción en Leal')
    puntos_activos = fields.Integer(string='Puntos Activos', help='Puntos activos del cliente')
    puntos = fields.Integer(string='Puntos', help='Puntos obtenidos en esta transacción')
    descuento_total = fields.Float(string='Descuento Total', help='Descuento total aplicado')
    no_factura = fields.Char(string='No. Factura', help='Número de factura')
    uid = fields.Char(string='UID', help='Identificador único de la transacción')
    
    # Campos adicionales para tracking
    pos_order_id = fields.Many2one('pos.order', string='Orden POS', help='Orden POS relacionada')
    customer_id = fields.Many2one('res.partner', string='Cliente', help='Cliente relacionado')
    response_data = fields.Text(string='Datos de Respuesta', help='JSON completo de la respuesta del API')
    
    # Campos de auditoría
    create_date = fields.Datetime(string='Fecha de Creación', default=fields.Datetime.now, readonly=True)
    create_uid = fields.Many2one('res.users', string='Creado por', default=lambda self: self.env.user, readonly=True)
    
    @api.model
    def create_from_api_response(self, response_data, pos_order=None, customer=None):
        """
        Crea un registro desde la respuesta del API de Leal
        
        Args:
            response_data (dict): Datos de respuesta del API
            pos_order (pos.order, optional): Orden POS relacionada
            customer (res.partner, optional): Cliente relacionado
            
        Returns:
            leal.accumulate.response: Registro creado
        """
        vals = {
            'code': response_data.get('code'),
            'id_transaccion': str(response_data.get('id_transaccion')),
            'puntos_activos': response_data.get('puntos_activos', 0),
            'puntos': response_data.get('puntos', 0),
            'descuento_total': response_data.get('descuentoTotal', 0.0),
            'no_factura': response_data.get('no_factura'),
            'uid': response_data.get('uid'),
            'response_data': str(response_data),
        }
        
        if pos_order:
            vals['pos_order_id'] = pos_order.id
            
        if customer:
            vals['customer_id'] = customer.id
            
        # Use sudo to ensure the system can persist external API responses
        return self.sudo().create(vals)
    
    def name_get(self):
        """
        Personaliza el nombre mostrado en las vistas
        """
        result = []
        for record in self:
            name = f"Transacción {record.id_transaccion} - {record.no_factura or 'Sin factura'}"
            result.append((record.id, name))
        return result