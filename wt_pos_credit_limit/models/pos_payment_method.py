from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PosPaymentMethod(models.Model):
    _inherit = "pos.payment.method"

    credit_journal = fields.Boolean(related='journal_id.credit_journal', store=False)

    @api.model
    def _load_pos_data_fields(self, config_id):
        fields = super()._load_pos_data_fields(config_id)
        fields += ['credit_journal']
        return fields