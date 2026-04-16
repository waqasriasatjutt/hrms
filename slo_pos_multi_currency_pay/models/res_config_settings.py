from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    currency_ids = fields.Many2many('res.currency',
                                    string="Currencies",
                                    related="pos_config_id.currency_ids",
                                    readonly=False,
                                    help="The list of currencies supported by "
                                         "this Point of Sale configuration.")

    enable_currency = fields.Boolean(string="Enable Currency",
                                     config_parameter="multi_currency_payment_in_pos.enable_currency",
                                     help="Enable or disable currency for "
                                          "this POS configuration.")

    @api.onchange('enable_currency')
    def _onchange_value(self):
        for rec in self:
            rec.pos_config_id.enable_multicurrency = rec.enable_currency
            print("onchange : ", rec.pos_config_id.enable_multicurrency)

