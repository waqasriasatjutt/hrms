from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SurveySurvey(models.Model):
    _name = 'survey.survey'
    _inherit = ['survey.survey', 'pos.load.mixin']

    survey_type = fields.Selection(
        selection_add=[('pos_survey', 'Pos Survey')],
        ondelete={'pos_survey': 'set default'}
    )
    pos_survey_timing = fields.Selection([
        ('order', 'After Order'),
        ('session', 'After Session'),
    ], required=True, default='order')
    config_ids = fields.Many2many('pos.config', string='Point of Sale')
    open_session_ids = fields.Many2many('pos.session', string='Pos Sessions', compute='_compute_open_session_ids', help='Open PoS sessions that are using this survey method.')
    enable_scoring = fields.Boolean(default=False)

    def write(self, vals):
        if self.open_session_ids:
            raise UserError(_('Please close and validate the following open PoS Sessions before modifying this survey.\n'
                            'Open sessions: %s', (' '.join(self.open_session_ids.mapped('name')),)))
        return super().write(vals)
    
    @api.depends('config_ids')
    def _compute_open_session_ids(self):
        for survey in self:
            survey.open_session_ids = self.env['pos.session'].search([('config_id', 'in', survey.config_ids.ids), ('state', '!=', 'closed')])

    def _get_compatible_qtypes(self):
        return [
            'simple_choice',
            'char_box',
            'text_box',
            'numerical_box',
        ]
    
    @api.onchange('enable_scoring')
    def _onchange_enable_scoring(self):
        self.scoring_type = 'scoring_without_answers' if self.enable_scoring else 'no_scoring'

    @api.onchange('survey_type')
    def _onchange_survey_type(self):
        super()._onchange_survey_type()
        if self.survey_type == 'pos_survey':

            for q in self.question_and_page_ids:
                if q.question_type not in self._get_compatible_qtypes:
                    q.unlink()
            self.write({
                'scoring_type': 'no_scoring',
                'certification': False,
                'is_time_limited': False,
                'session_speed_rating': False,
            })

    @api.model
    def _load_pos_data_domain(self, data):
        config_id = self.env['pos.config'].browse(data['pos.config']['data'][0]['id'])
        return [
            ('survey_type', '=', 'pos_survey'),
            ('id', 'in', config_id.survey_ids.ids),
        ]

    @api.model
    def _load_pos_data_fields(self, config_id):
        return ['title', 'id', 'pos_survey_timing']
