from odoo import models, fields, api, _


class SurveyQuestion(models.Model):
    _name = 'survey.question'
    _inherit = ['survey.question', 'pos.load.mixin']

    pos_question_type = fields.Selection([
        ('simple_choice', 'Multiple choice: only one answer'),
        ('char_box', 'Single Line Text Box'),
        ('text_box', 'Multiple Lines Text Box'),
        ('numerical_box', 'Numerical Value'),
    ], default="simple_choice")
    pos_config_ids = fields.Many2many('pos.config', compute='_compute_pos_config_ids')

    survey_type = fields.Selection(related='survey_id.survey_type')

    def _compute_pos_config_ids(self):
        for q in self:
            q.pos_config_ids = q.survey_id.config_ids

    @api.onchange('pos_question_type')
    def _onchange_pos_question_type(self):
        self.question_type = self.pos_question_type

    @api.model
    def _load_pos_data_domain(self, data):
        config_id = self.env['pos.config'].browse(data['pos.config']['data'][0]['id'])
        return [
            ('survey_id', 'in', config_id.survey_ids.ids),
        ]

    @api.model
    def _load_pos_data_fields(self, config_id):
        return [
            'title', 'survey_id', 'sequence', 'id', 'question_type', 'constr_mandatory', 
            'answer_score', 'answer_numerical_box', 'question_placeholder',
        ]


class SurveyQuestionAnswer(models.Model):
    _name = 'survey.question.answer'
    _inherit = ['survey.question.answer', 'pos.load.mixin']

    pos_config_ids = fields.Many2many('pos.config', compute='_compute_pos_config_ids')

    def _compute_pos_config_ids(self):
        for qa in self:
            qa.pos_config_ids = qa.question_id.survey_id.config_ids

    @api.model
    def _load_pos_data_domain(self, data):
        config_id = self.env['pos.config'].browse(data['pos.config']['data'][0]['id'])
        return [
            ('question_id.survey_id', 'in', config_id.survey_ids.ids),
        ]

    @api.model
    def _load_pos_data_fields(self, config_id):
        return [
            'value', 'question_id', 'answer_score'
        ]
