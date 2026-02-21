
from odoo import fields, models

class RecruitmentQuestionAnswer(models.Model):
    _name = 'recruitment.question.answer'
    _description = 'Question Answer Option'
    _rec_name = 'value'

    question_id = fields.Many2one('recruitment.question', ondelete='cascade')
    value = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    is_correct = fields.Boolean()
