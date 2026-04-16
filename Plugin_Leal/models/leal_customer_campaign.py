# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class LealCustomerCampaign(models.Model):
    _name = 'leal.customer.campaign'
    _description = 'Leal Customer Campaign'
    _rec_name = 'campaign_name'

    # Campos principales de la campaña
    rule_type = fields.Selection([
        ('category', 'Category'),
        ('product', 'Product'),
        ('order', 'Order')
    ], string='Rule Type', required=True)
    
    requirement_id = fields.Char(string='Requirement ID')
    minimum_amount = fields.Float(string='Minimum Amount')
    minimum_quantity = fields.Integer(string='Minimum Quantity')
    benefit_unit_limit = fields.Integer(string='Benefit Unit Limit')
    
    reward_type = fields.Selection([
        ('discount', 'Discount'),
        ('product', 'Product')
    ], string='Reward Type', required=True)
    
    reward = fields.Char(string='Reward')
    max_discount_amount = fields.Float(string='Max Discount Amount')
    
    # Información de la campaña
    campaign_id = fields.Integer(string='Campaign ID', required=True)
    promotion_code = fields.Char(string='Promotion Code')
    start_date = fields.Datetime(string='Start Date')
    end_date = fields.Datetime(string='End Date')
    campaign_name = fields.Char(string='Campaign Name', required=True)
    campaign_description = fields.Text(string='Campaign Description')
    
    # Campos de control
    customer_uid = fields.Char(string='Customer UID', required=True)
    pos_config_id = fields.Integer(string='POS Config ID', required=True)
    active = fields.Boolean(string='Active', default=True)
    created_date = fields.Datetime(string='Created Date', default=fields.Datetime.now)
    
    @api.model
    def delete_customer_campaigns(self, customer_uid, pos_config_id):
        """
        Elimina todas las campañas asociadas a un cliente específico en un punto de venta.
        """
        campaigns = self.search([
            ('customer_uid', '=', customer_uid),
            ('pos_config_id', '=', pos_config_id)
        ])
        deleted_count = len(campaigns)
        campaigns.unlink()
        return {
            'success': True,
            'message': f'Se eliminaron {deleted_count} campañas para el cliente {customer_uid}'
        }
    
    @api.model
    def save_customer_campaigns(self, customer_uid, campaigns_data, pos_config_id):
        """
        Guarda las campañas de un cliente específico para un punto de venta.
        Elimina las campañas existentes del cliente en ese punto de venta y crea las nuevas.
        """
        # Eliminar campañas existentes del cliente en este punto de venta
        existing_campaigns = self.search([
            #('customer_uid', '=', customer_uid),
            ('pos_config_id', '=', pos_config_id)
        ])
        existing_campaigns.unlink()
        
        # Crear las nuevas campañas
        campaigns_to_create = []
        for campaign_data in campaigns_data:
            campaign_vals = {
                'customer_uid': customer_uid,
                'pos_config_id': pos_config_id,
                'rule_type': campaign_data.get('rule_type'),
                'requirement_id': campaign_data.get('requirement_id', ''),
                'minimum_amount': campaign_data.get('minimum_amount', 0.0),
                'minimum_quantity': campaign_data.get('minimum_quantity', 0),
                'benefit_unit_limit': campaign_data.get('benefit_unit_limit', 0),
                'reward_type': campaign_data.get('reward_type'),
                'reward': campaign_data.get('reward', ''),
                'max_discount_amount': campaign_data.get('max_discount_amount', 0.0),
                'campaign_id': campaign_data.get('campaign_id'),
                'promotion_code': campaign_data.get('promotion_code', ''),
                'start_date': self._parse_datetime(campaign_data.get('start_date')),
                'end_date': self._parse_datetime(campaign_data.get('end_date')),
                'campaign_name': campaign_data.get('campaign_name', ''),
                'campaign_description': campaign_data.get('campaign_description', ''),
            }
            campaigns_to_create.append(campaign_vals)
        
        # Crear los registros
        if campaigns_to_create:
            created_campaigns = self.create(campaigns_to_create)
            return {
                'success': True,
                'message': f'Se guardaron {len(created_campaigns)} campañas para el cliente {customer_uid}',
                'campaign_ids': created_campaigns.ids
            }
        else:
            return {
                'success': True,
                'message': 'No hay campañas para guardar',
                'campaign_ids': []
            }
    
    def _parse_datetime(self, date_string):
        """
        Convierte una fecha en formato ISO a datetime de Odoo (naive datetime)
        """
        if not date_string:
            return False
        try:
            # Formato: "2025-07-10T00:00:00Z"
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            # Convertir a naive datetime (sin zona horaria) para Odoo
            return dt.replace(tzinfo=None)
        except (ValueError, AttributeError):
            return False
    
    @api.model
    def get_customer_campaigns(self, customer_uid):
        """
        Obtiene todas las campañas activas de un cliente
        """
        campaigns = self.search([
            ('customer_uid', '=', customer_uid),
            ('active', '=', True)
        ])
        
        return campaigns.read([
            'rule_type', 'requirement_id', 'minimum_amount', 'minimum_quantity',
            'benefit_unit_limit', 'reward_type', 'reward', 'max_discount_amount',
            'campaign_id', 'promotion_code', 'start_date', 'end_date',
            'campaign_name', 'campaign_description'
        ])
    
    @api.model
    def get_active_campaigns_by_type(self, customer_uid, rule_type):
        """
        Obtiene campañas activas de un cliente filtradas por tipo de regla
        """
        campaigns = self.search([
            ('customer_uid', '=', customer_uid),
            ('rule_type', '=', rule_type),
            ('active', '=', True),
            ('start_date', '<=', fields.Datetime.now()),
            ('end_date', '>=', fields.Datetime.now())
        ])
        
        return campaigns.read([
            'rule_type', 'requirement_id', 'minimum_amount', 'minimum_quantity',
            'benefit_unit_limit', 'reward_type', 'reward', 'max_discount_amount',
            'campaign_id', 'promotion_code', 'campaign_name', 'campaign_description'
        ])