
{
    'name': 'Recruitment Interview Questions (Survey Style)',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Survey-style interview questions with candidate answers',
    'depends': ['hr','hr_recruitment'],
    'data': [
        'security/ir.model.access.csv',
        'views/website_hr_recruitment_questions_templates.xml',
        'views/recruitment_question_views.xml',
        'views/hr_job_views.xml',
        'views/hr_applicant_views.xml',
        # 'views/candidate_answer_views.xml',
    ],
    'installable': True,
}
