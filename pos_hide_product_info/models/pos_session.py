from odoo import api, fields, models


class POSSession(models.Model):
    _inherit = "pos.session"

    pos_hide_product_info = fields.Boolean(string="Hide Product 'Info' Button",
                                       related="config_id.pos_hide_product_info", readonly=False)

    def _loader_params_pos_session(self):
        result = super(POSSession, self)._loader_params_pos_session()
        result['search_params']['fields'].extend(['pos_hide_product_info'])
        return result
