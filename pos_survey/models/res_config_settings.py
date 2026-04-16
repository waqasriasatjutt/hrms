from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    survey_ids = fields.Many2many(
        'survey.survey', 
        related='pos_config_id.survey_ids', 
        readonly=False, 
        domain=[('survey_type', '=', 'pos_survey')]
    )
