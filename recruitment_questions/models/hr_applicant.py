from odoo import models, fields

class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    candidate_answer_ids = fields.One2many(
        'recruitment.candidate.answer',
        'applicant_id',
        string='Candidate Answers'
    )
