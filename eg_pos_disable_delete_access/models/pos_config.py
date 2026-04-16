from odoo import models, fields, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    eg_pos_disable_delete_access_enable = fields.Boolean(string="POS Disable Delete Access", default=True)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    eg_pos_disable_delete_access_enable = fields.Boolean(string="POS Disable Delete Access",
                                                         related="pos_config_id.eg_pos_disable_delete_access_enable",
                                                         readonly=False
                                                         )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        icp = self.env['ir.config_parameter'].sudo()
        res.update(
            eg_pos_disable_delete_access_enable=icp.get_param(
                'eg_pos_disable_delete_access.eg_pos_disable_delete_access_enable'))
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        icp = self.env['ir.config_parameter'].sudo()
        icp.set_param('eg_pos_disable_delete_access.eg_pos_disable_delete_access_enable',
                      self.eg_pos_disable_delete_access_enable)
