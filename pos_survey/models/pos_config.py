from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    survey_ids = fields.Many2many(
        'survey.survey',
        domain=[('survey_type', '=', 'pos_survey')],
    )

    def _get_forbidden_change_fields(self):
        res = super()._get_forbidden_change_fields()
        res.extend([
            'survey_ids',
        ])
        return res
