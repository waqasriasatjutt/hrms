from odoo import api, fields, models, _

class PosConfig(models.Model):
    _inherit = 'pos.config'

    default_pos_partner_id = fields.Many2one('res.partner',string="Customer", help="Automatically selects the customer in POS")
    