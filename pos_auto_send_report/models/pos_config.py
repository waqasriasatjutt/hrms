from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    send_auto_email = fields.Char(
        string="Email",
        help="Enter the email address to which the order validation email should be sent.",
        required=False,
        readonly=False,
        index=True
    )


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _pos_ui_models_to_load(self):
        res = super()._pos_ui_models_to_load()
        print(res,'.......res')
        return res

    def _loader_params_pos_config(self):
        result = super()._loader_params_pos_config()
        result['fields'].append('send_auto_email')  # Add the email field
        return result