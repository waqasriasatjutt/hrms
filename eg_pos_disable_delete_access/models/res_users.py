from odoo import fields, models, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    disable_delete_access = fields.Boolean(string="Disable Delete Access")
    is_display_details = fields.Boolean("Display Details", compute='_compute_is_display')

    def _compute_is_display(self):
        for rec in self:
            rec.is_display_details = self.env['ir.config_parameter'].sudo().get_param(
                'eg_pos_disable_delete_access.eg_pos_disable_delete_access_enable')

    @api.model
    def _load_pos_data_fields(self, config_id):
        result = super()._load_pos_data_fields(config_id)
        result.append('disable_delete_access')
        return result

    def manager_validation(self, pos_config_id):
        pos_config_id = self.env["pos.config"].search([("id", '=', pos_config_id)], limit=1)
        manager_list = []
        for manager_id in pos_config_id.manager_ids:
            manager_list.append({
                'id': manager_id.id,
                'name': manager_id.display_name,
                'pin': manager_id.manager_pin,
                'password': manager_id.manager_password,
            })
        return manager_list
