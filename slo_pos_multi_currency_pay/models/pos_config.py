from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    currency_ids = fields.Many2many('res.currency',
                                    string='Currency', help='Currency')
    enable_multicurrency = fields.Boolean(string='Enable  multi currency',
                                          help='Enable the multi currency')

    @api.model
    def get_config_settings(self, config_id):
        """Updating all the currencies with id, name, symbol, rate"""
        config = self.env['pos.config'].browse(int(config_id))
        result = []
        for currency in config.currency_ids:
            result.append({
                'id': currency.id,
                'name': currency.name,
                'symbol': currency.symbol,
                'rate': currency.rate,
            })

        return result

    @api.model
    def get_selected_currency(self, selected_id):
        """Return the """
        currency = self.env['res.currency'].browse(int(selected_id))
        usd_val = round(1 / currency.rate, 2)
        return [{
            'id': currency.id,
            'name': currency.name,
            'symbol': currency.symbol,
            'rate': currency.rate,
            'usd_val': usd_val
        }]
