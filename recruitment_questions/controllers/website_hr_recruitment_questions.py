from odoo import http
from odoo.addons.website_hr_recruitment.controllers.main import WebsiteHrRecruitment
from odoo.http import request
from odoo.exceptions import ValidationError


# class WebsiteHrRecruitmentQuestions(http.Controller):
class WebsiteHrRecruitmentQuestions(WebsiteHrRecruitment):

    @http.route(
        '/jobs/<model("hr.job"):job>/questions',
        type='http',
        auth='public',
        website=True,
        sitemap=True
    )
    def job_questions(self, job, **kwargs):
        questions = job.sudo().question_ids.sorted('sequence')
        template = request.env.ref('recruitment_questions.apply_with_questions', raise_if_not_found=True)
        return request.render(template.id, {
            'job': job,
            'questions': questions,
        })

    def extract_data(self, model, values):
        data = super().extract_data(model, values)

        if model.sudo().model != 'hr.applicant':
            return data

        job_id = values.get('job_id')
        if not job_id:
            return data

        job = request.env['hr.job'].sudo().browse(int(job_id))
        answers_to_create = []

        for question in job.question_ids:

            qname = f'question_{question.id}'
            has_answer = False

            # ===============================
            # SIMPLE CHOICE / SCALE
            # ===============================
            if question.question_type in ('simple_choice', 'scale'):
                val = values.get(qname)
                if val:
                    has_answer = True
                    answers_to_create.append((0, 0, {
                        'question_id': question.id,
                        'selected_answer_id': int(val),
                    }))

            # ===============================
            # MULTIPLE CHOICE
            # ===============================
            elif question.question_type == 'multiple_choice':
                for ans in question.answer_ids:
                    if values.get(f'{qname}_{ans.id}'):
                        has_answer = True
                        answers_to_create.append((0, 0, {
                            'question_id': question.id,
                            'selected_answer_id': ans.id,
                        }))

            # ===============================
            # TEXT TYPES
            # ===============================
            elif question.question_type in (
                    'text_box', 'char_box',
                    'numerical_box', 'date', 'datetime'
            ):
                val = values.get(qname)
                if val and str(val).strip():
                    has_answer = True
                    answers_to_create.append((0, 0, {
                        'question_id': question.id,
                        'text_answer': val,
                    }))

            # ===============================
            # 🔴 MANDATORY CHECK
            # ===============================
            if question.constr_mandatory and not has_answer:
                raise ValidationError(
                    f"The question '{question.title}' is mandatory. Please answer it before submitting."
                )

        if answers_to_create:
            data['record']['candidate_answer_ids'] = answers_to_create

        return data

    # def extract_data(self, model, values):
    #     data = super().extract_data(model, values)
    #
    #     if model.sudo().model != 'hr.applicant':
    #         return data
    #
    #     job_id = values.get('job_id')
    #     if not job_id:
    #         return data
    #
    #     job = request.env['hr.job'].sudo().browse(int(job_id))
    #     answers_to_create = []
    #
    #     for question in job.question_ids:
    #         qname = f'question_{question.id}'
    #
    #         # SINGLE CHOICE / SCALE
    #         if question.question_type in ('simple_choice', 'scale'):
    #             val = values.get(qname)
    #             if val:
    #                 answers_to_create.append((0, 0, {
    #                     'question_id': question.id,
    #                     'selected_answer_id': int(val),
    #                 }))
    #
    #         # MULTIPLE CHOICE
    #         elif question.question_type == 'multiple_choice':
    #             for ans in question.answer_ids:
    #                 if values.get(f'{qname}_{ans.id}'):
    #                     answers_to_create.append((0, 0, {
    #                         'question_id': question.id,
    #                         'selected_answer_id': ans.id,
    #                     }))
    #
    #         # TEXT TYPES
    #         elif question.question_type in (
    #                 'text_box', 'char_box', 'numerical_box', 'date', 'datetime'
    #         ):
    #             val = values.get(qname)
    #             if val:
    #                 answers_to_create.append((0, 0, {
    #                     'question_id': question.id,
    #                     'text_answer': val,
    #                 }))
    #
    #
    #         # elif question.question_type == 'matrix':
    #         #     for row in question.answer_ids:
    #         #         val = values.get(f'matrix_{question.id}_{row.id}')
    #         #         if val:
    #         #             answers_to_create.append((0, 0, {
    #         #                 'question_id': question.id,
    #         #                 'text_answer': f'Row {row.value}: {val}',
    #         #             }))
    #
    #     # Attach answers directly to applicant
    #     if answers_to_create:
    #         data['record']['candidate_answer_ids'] = answers_to_create
    #
    #     return data