from odoo import models, fields, api, _


class PosOrder(models.Model):
    _inherit = 'pos.order'

    pos_survey_answer_ids = fields.One2many('survey.user_input.line', 'pos_order_id')
    participation_ids = fields.One2many('survey.user_input', 'pos_order_id')
    survey_answers_count = fields.Integer(compute='_compute_survey_answers_count')

    def _compute_survey_answers_count(self):
        for order in self:
            order.survey_answers_count = len(order.pos_survey_answer_ids)

    def _create_or_update_survey_answers(self, answers):
        for answer in answers:
            survey_id = self.env['survey.survey'].browse(int(answer['survey_id']))
            participation_id = self.participation_ids.filtered(lambda p: p.survey_id == survey_id) or \
                    survey_id._create_answer(
                        user=self.session_id.user_id, 
                        pos_order_id=self.id,
                        employee_id=self.employee_id.id)
            participation_id = participation_id[0] if participation_id else False
            question_id = self.env['survey.question'].browse(int(answer['question_id']))
            participation_id._save_lines(question_id, answer['display_name'])
            participation_id.state='done'

    def action_view_survey_answers(self):
        return {
            'name': _('Survey Answers'),
            'view_mode': 'list',
            'view_id': self.env.ref('pos_survey.view_pos_survey_answer_list').id,
            'res_model': 'survey.user_input.line',
            'domain': [('pos_order_id', '=', self.id)],
            'type': 'ir.actions.act_window',
        }
    
    def process_survey(self, answers):
        """
            Register a new survey participation
        """
        self.sudo()._create_or_update_survey_answers(answers)
