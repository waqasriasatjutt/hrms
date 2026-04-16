from odoo import models, fields, api, _


class PosSession(models.Model):
    _inherit = 'pos.session'

    pos_survey_answer_ids = fields.One2many('survey.user_input.line', 'pos_session_id')
    participation_ids = fields.One2many('survey.user_input', 'pos_session_id')
    survey_answers_count = fields.Integer(compute='_compute_survey_answers_count')

    def action_view_survey_answers(self):
        return {
            'name': _('Survey Answers'),
            'view_mode': 'list',
            'view_id': self.env.ref('pos_survey.view_pos_survey_answer_list').id,
            'res_model': 'survey.user_input.line',
            'domain': [('pos_session_id', '=', self.id)],
            'type': 'ir.actions.act_window',
        }

    def _compute_survey_answers_count(self):
        for session in self:
            session.survey_answers_count = len(session.pos_survey_answer_ids)

    @api.model
    def _load_pos_data_models(self, config_id):
        data = super()._load_pos_data_models(config_id)
        data += ['survey.survey', 'survey.question', 'survey.question.answer', 'survey.user_input.line']
        return data

    def _create_or_update_survey_answers(self, answers):
        for answer in answers:
            survey_id = self.env['survey.survey'].browse(int(answer['survey_id']))
            participation_id = self.participation_ids.filtered(lambda p: p.survey_id == survey_id) or \
                    survey_id._create_answer(
                        user=self.user_id,
                        pos_session_id=self.id)
            participation_id = participation_id[0] if participation_id else False
            question_id = self.env['survey.question'].browse(int(answer['question_id']))
            participation_id._save_lines(question_id, answer['display_name'])
            participation_id.state='done'

    def process_survey(self, answers):
        self._create_or_update_survey_answers(answers)
