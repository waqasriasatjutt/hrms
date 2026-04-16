from odoo import api, fields, models, _


class PosPaymentMethod(models.Model):
    _inherit = "pos.payment.method"

    card_id = fields.Many2one(
        "account.card",
        string="Card",
    )
    instalment_product_id = fields.Many2one(
        "product.product",
        string="Producto Recargo Financiero",
    )

    instalment_ids = fields.One2many(
        "account.card.installment",
        string="Instalments",
        related="card_id.installment_ids",
    )

    @api.model
    def _load_pos_data_domain(self, data):
        params = super()._load_pos_data_domain(data)
        return params

    @api.model
    def _load_pos_data_fields(self, config_id):
        params = super()._load_pos_data_fields(config_id)
        params += [
            'id', 'card_id', 'instalment_product_id', 'instalment_ids'
        ]
        return params

    def _load_pos_data(self, data):
        domain = self._load_pos_data_domain(data)
        fields = self._load_pos_data_fields(data['pos.config']['data'][0]['id'])
        return {
            'data': self.search_read(domain, fields, load=False) if domain is not False else [],
            'fields': fields,
        }
