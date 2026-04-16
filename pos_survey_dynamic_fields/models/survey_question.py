from odoo import models, fields, api, _


class SurveyQuestion(models.Model):
    _inherit = 'survey.question'

    is_dynamic = fields.Boolean(default=False)
    dynamic_field_type = fields.Selection([
        ('time', 'Time'),
        ('weekday', 'Weekday'),
        ('guest_number', 'Guest Number'),
    ])

    def write(self, vals):
        res = super().write(vals)
        [option._validate_options() for option in self.suggested_answer_ids]
        return res

    @api.model
    def _load_pos_data_fields(self, config_id):
        return super()._load_pos_data_fields(config_id) + ['is_dynamic', 'dynamic_field_type']
    
    @api.onchange('is_dynamic', 'dynamic_field_type')
    def _onchange_dynamic(self):
        if self.is_dynamic:
            set_default = getattr(self, f'_set_default_for_dynamic_{self.dynamic_field_type}', None)
            if set_default:
                set_default()
            else:
                self.write({
                    'suggested_answer_ids': [
                        (5, 0, 0), 
                    ]
                })
        else:
            self.dynamic_field_type = False

    def _set_default_for_dynamic_weekday(self):
        if not self.is_dynamic and not self.dynamic_field_type == 'weekday':
            return
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        options = [(0, 0, {
                'value': weekday,
                'is_correct': True,
                'answer_score': 0,
            }) for weekday in weekdays
        ]
        self.write({
            'title': 'Weekday',
            'question_type': 'simple_choice',
            'suggested_answer_ids': [
                (5, 0, 0), 
                *options
            ]
        })

    def _set_default_for_dynamic_time(self):
        self.write({
            'title': 'Time',
            'question_type': 'simple_choice',
            'suggested_answer_ids': [
                (5, 0, 0), 
            ]
        })

    def _set_default_for_dynamic_guest_number(self):
        self.write({
            'title': 'Guest Number',
            'question_type': 'simple_choice',
            'suggested_answer_ids': [
                (5, 0, 0), 
            ]
        })
