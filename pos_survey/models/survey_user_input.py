from odoo import models, fields, api, _


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    pos_order_id = fields.Many2one('pos.order', ondelete='restrict')
    pos_session_id = fields.Many2one('pos.session', ondelete='restrict')
    employee_id = fields.Many2one('hr.employee', string='Filled By')


class SurveyUserInputLine(models.Model):
    _name = 'survey.user_input.line'
    _inherit = ['survey.user_input.line', 'pos.load.mixin']

    pos_order_id = fields.Many2one('pos.order', related='user_input_id.pos_order_id', store=True)
    pos_session_id = fields.Many2one('pos.session', related='user_input_id.pos_session_id', store=True)

    @api.model
    def _load_pos_data_domain(self, data):
        config_id = self.env['pos.config'].browse(data['pos.config']['data'][0]['id'])
        return [
            ('question_id', '=', config_id.survey_ids.question_ids.ids),
            ('survey_id', 'in', config_id.survey_ids.ids),
        ]

    @api.model
    def _load_pos_data_fields(self, config_id):
        return ['display_name', 'suggested_answer_id', 'survey_id', 'question_id', 'pos_order_id']
