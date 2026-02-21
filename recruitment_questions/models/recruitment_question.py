from odoo import api, fields, models, tools, _

class RecruitmentQuestion(models.Model):
    _name = 'recruitment.question'
    _description = 'Recruitment Question'
    _order = 'sequence, id'
    _rec_name = 'title'   # ✅ ADD THIS

    title = fields.Char(required=True)
    sequence = fields.Integer(default=10)

    is_page = fields.Boolean('Is a page?')

    question_type = fields.Selection(
        selection=[
            ('simple_choice', 'Multiple choice: only one answer'),
            ('multiple_choice', 'Multiple choice: multiple answers allowed'),
            ('text_box', 'Multiple Lines Text Box'),
            ('char_box', 'Single Line Text Box'),
            ('numerical_box', 'Numerical Value'),
            ('scale', 'Scale'),
            ('date', 'Date'),
            ('datetime', 'Datetime'),
            # ('matrix', 'Matrix')
        ],
        string='Question Type',
        default='simple_choice',  # <-- default ensures it always has a value
        required=True
    )
    # question_type = fields.Selection(
    #     selection=[
    #         ('simple_choice', 'Multiple choice: only one answer'),
    #         ('multiple_choice', 'Multiple choice: multiple answers allowed'),
    #         ('text_box', 'Multiple Lines Text Box'),
    #         ('char_box', 'Single Line Text Box'),
    #         ('numerical_box', 'Numerical Value'),
    #         ('scale', 'Scale'),
    #         ('date', 'Date'),
    #         ('datetime', 'Datetime'),
    #         ('matrix', 'Matrix')
    #     ],
    #     string='Question Type',
    #     default='simple_choice',  # <-- default ensures it always has a value
    #     required=True
    # )

    @api.depends('is_page')
    def _compute_question_type(self):
        pages = self.filtered(lambda question: question.is_page)
        pages.question_type = False
        (self - pages).filtered(lambda question: not question.question_type).question_type = 'simple_choice'


    answer_ids = fields.One2many(
        'recruitment.question.answer',
        'question_id',
        string="Answers"
    )

    job_ids = fields.Many2many(
        'hr.job',
        string='Job Positions'
    )
    constr_mandatory = fields.Boolean('Mandatory Answer')

