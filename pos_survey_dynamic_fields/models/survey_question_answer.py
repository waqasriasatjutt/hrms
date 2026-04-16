from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
import re

from datetime import datetime

class SurveyQuestionAnswer(models.Model):
    _inherit = 'survey.question.answer'

    def _get_non_editable_dynamic_fields(self):
        return [
            'weekday',
        ]
    
    def _validate_options(self):
        if not self.question_id.is_dynamic:
            return
        validate_method = getattr(self, f'_validate_{self.question_id.dynamic_field_type}', None)
        if validate_method:
            validate_method()

    def _validate_time(self):
        """Time options will be evaluated to True or False.

        The format must be <operator><24h time format> or <24h time format><operator><24h time format>.
        Allowed operators:
            > greater than
            >= greater than or equal to
            < less than
            <= less than or equal to
            = equals
            <> is between

        Examples:
            >15:00 evaluates to greater than 15:00.
            10:30<>13:00 evaluates to between 10:30 and 13:00.
        """
        time_pattern = r'^(>|>=|<|<=|=)?(([01]\d|2[0-3]):([0-5]\d))(<>(([01]\d|2[0-3]):([0-5]\d)))?$'

        if not re.match(time_pattern, self.value):
            raise ValidationError("Invalid time format. Must be in the format '<operator><time>' or '<time><operator><time>'.")

        # Check for "between" condition (e.g., 10:00<>15:00)
        between_match = re.match(r'(([01]\d|2[0-3]):([0-5]\d))(<>(([01]\d|2[0-3]):([0-5]\d)))?$', self.value)
        
        if between_match:
            low_value = between_match.groups()[0]
            high_value = between_match.groups()[4]
            low_time = self._convert_to_time(low_value)
            high_time = self._convert_to_time(high_value)
            
            if low_time >= high_time:
                raise ValidationError("The first time must be less than the second time.")

    @staticmethod
    def _convert_to_time(string):
        return datetime.strptime(string, "%H:%M").time()

    def _validate_weekday(self):
        """Weekday options will be evaluated to True or False.

        The format must be one of the weekdays written in full (e.g., 'Monday', 'Tuesday', etc.).
        """
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        if self.value not in weekdays:
            raise ValidationError(f"Invalid weekday. Must be one of: {', '.join(weekdays)}.")

    def _validate_guest_number(self):
        """Guest number must evaluate to True or False. The number set must also be an integer.

        The format must be <operator><integer> or <integer><operator><integer>.
        Allowed operators:
            > greater than
            >= greater than or equal to
            < less than
            <= less than or equal to
            = equals
            <> is between

        Examples:
            >1 evaluates to greater than 1.
            5<>15 evaluates to between 5 and 15.
        """
        guest_number_pattern = r'^(>|>=|<|<=|=)?(\d+)(<>(\d+))?$'
        
        # Validate the format of the guest number
        if not re.match(guest_number_pattern, self.value):
            raise ValidationError(
                "Invalid guest number format. Must be in the format '<operator><integer>' or '<integer><operator><integer>'."
            )

        # Extract the values and operators from the pattern
        between_match = re.search(r'(\d+)(<>(\d+))', self.value)

        # Check if it's a "between" condition
        if between_match:
            low_value = int(between_match.groups()[0])
            high_value = int(between_match.groups()[2])
            if low_value >= high_value:
                raise ValidationError("The first number must be less than the second number.")
