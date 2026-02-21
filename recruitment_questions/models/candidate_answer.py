
from odoo import fields, models

class CandidateAnswer(models.Model):
    _name = 'recruitment.candidate.answer'
    _description = 'Candidate Answer'

    applicant_id = fields.Many2one('hr.applicant', required=True)
    question_id = fields.Many2one('recruitment.question', required=True)
    text_answer = fields.Text()
    selected_answer_id = fields.Many2one('recruitment.question.answer')
