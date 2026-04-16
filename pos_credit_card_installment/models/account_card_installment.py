from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class AccountCard(models.Model):
    _inherit = 'account.card'

    @api.model
    def _load_pos_data_domain(self, data):
        return [('active', '=', True)]

    @api.model
    def _load_pos_data_fields(self, config_id):
        return ['id', 'name', 'installment_ids', 'active']

    def _load_pos_data(self, data):
        domain = self._load_pos_data_domain(data)
        fields = self._load_pos_data_fields(data['pos.config']['data'][0]['id'])
        result = self.search_read(domain, fields, load=False) if domain is not False else []
        _logger.info(f"Loading account.card data: {len(result)} records found")
        for card in result:
            _logger.info(f"  Card {card['id']}: {card['name']}")
        return {
            'data': result,
            'fields': fields,
        }


class AccountCardInstallment(models.Model):
    _inherit = 'account.card.installment'

    @api.model
    def _load_pos_data_domain(self, data):
        return [('active', '=', True)]

    @api.model
    def _load_pos_data_fields(self, config_id):
        return [
            'id', 'name', 'installment', 'surcharge_coefficient', 
            'divisor', 'card_id', 'bank_discount', 'active'
        ]

    def _load_pos_data(self, data):
        domain = self._load_pos_data_domain(data)
        fields = self._load_pos_data_fields(data['pos.config']['data'][0]['id'])
        result = self.search_read(domain, fields, load=False) if domain is not False else []
        _logger.info(f"Loading account.card.installment data: {len(result)} records found")
        for installment in result:
            _logger.info(f"  Installment {installment['id']}: {installment['installment']} cuotas, card_id={installment['card_id']}")
        return {
            'data': result,
            'fields': fields,
        }