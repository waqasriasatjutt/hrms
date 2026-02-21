from odoo import models, fields

class HrJob(models.Model):
    _inherit = 'hr.job'

    question_ids = fields.Many2many(
        'recruitment.question',
        'recruitment_question_job_rel',
        'job_id',
        'question_id',
        string="Interview Questions"
    )
