/** @odoo-module */

import { PosSurveyPopup } from "@pos_survey/app/pos_survey_popup/pos_survey_popup";
import { patch } from "@web/core/utils/patch";
import { usePos } from "@point_of_sale/app/store/pos_hook";


patch(PosSurveyPopup.prototype, {

    setup() {
        this.dynamicQuestions = []
        super.setup(...arguments);
        this.pos = usePos();
    },

    buildSurveyData(surveys, survey_questions, survey_options, survey_answers) {
        const res = super.buildSurveyData(...arguments)
        const dynamic_questions = {};
        survey_questions.forEach(question => {
            if (question.is_dynamic) {
                dynamic_questions[question.id] = question.dynamic_field_type;
            }
        });

        // seperate out the standard from dynamic questions. 
        // Dynamic shouldnt show but be evaluated implicitly
        for (const survey of res) {
            var { questions } = survey
            var standardQuestions=[]
            questions.forEach(question => {
                if (question.question_id in dynamic_questions) {
                    question.dynamic_field_type = dynamic_questions[question.question_id]
                    question.is_dynamic = true
                    question.survey_id = survey.survey_id
                    this.dynamicQuestions.push(question)
                } else {
                    question.dynamic_field_type = null
                    question.is_dynamic = false
                    standardQuestions.push(question)
                }
            survey.questions = standardQuestions
            });
        }
        return res
    },

    _evaluate_time_condition(optionName) {
        const currentTime = new Date();
    
        // Check for "between" condition (e.g., "10:00<>15:00")
        const betweenMatch = optionName.match(/(([01]\d|2[0-3]):([0-5]\d))(<>(([01]\d|2[0-3]):([0-5]\d)))/);
        const operatorMatch = optionName.match(/^(>|>=|<|<=|=)?(([01]\d|2[0-3]):([0-5]\d))(<>(([01]\d|2[0-3]):([0-5]\d)))?$/);
        
        if (betweenMatch) {
            const lowValue = this.convertToTime(betweenMatch[1]);
            const highValue = this.convertToTime(betweenMatch[5]);
            return lowValue <= currentTime && currentTime <= highValue;
        } else if (operatorMatch) {
            const operator = operatorMatch[1];
            const timeValue = this.convertToTime(operatorMatch[2]);
    
            switch (operator) {
                case '>':
                    return currentTime > timeValue;
                case '>=':
                    return currentTime >= timeValue;
                case '<':
                    return currentTime < timeValue;
                case '<=':
                    return currentTime <= timeValue;
                case '=':
                    return currentTime === timeValue;
                default:
                    return false // better to just skip as the data cant be parsed
            }
        }
        return false // better to just skip as the data cant be parsed
    },
    
    _evaluate_guest_number_condition(optionName) {
        // Check for "between" condition (e.g., "5<>15")
        if (!this.pos.config.module_pos_restaurant) {
            return false
        }
        const currentGuestCount = this.pos.get_order().getCustomerCount()
        const betweenMatch = optionName.match(/(\d+)(<>(\d+))/);
        const operatorMatch = optionName.match(/(>|>=|<|<=|=)?(\d+)(<>(\d+))?$/);
        if (betweenMatch) {
            const lowValue = parseInt(betweenMatch[1], 10);
            const highValue = parseInt(betweenMatch[3], 10);
            return lowValue <= currentGuestCount && currentGuestCount <= highValue;
        } else if (operatorMatch) {
            const operator = operatorMatch[1];
            const guestNumber = parseInt(operatorMatch[2], 10);
    
            switch (operator) {
                case '>':
                    return currentGuestCount > guestNumber;
                case '>=':
                    return currentGuestCount >= guestNumber;
                case '<':
                    return currentGuestCount < guestNumber;
                case '<=':
                    return currentGuestCount <= guestNumber;
                case '=':
                    return currentGuestCount === guestNumber;
                default:
                    return false; // better to just skip as the data cant be parsed
            }
        }
        return false; // better to just skip as the data cant be parsed
    },
    
    convertToTime(timeStr) {
        const [hours, minutes] = timeStr.split(':').map(Number);
        return new Date(0, 0, 0, hours, minutes); // Create a Date object for comparison
    },

    _evaluate_weekday_condition(weekday) {
        const currentDate = new Date();
        const dayOfWeek = currentDate.getDay();
        const weekdays = [
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday"
        ];

        const currentWeekday = weekdays[dayOfWeek];

        return currentWeekday == weekday
    },

    _get_multichoice_question_types() {
        return [
            'simple_choice',
        ]
    },
    
    _exportSurveyAnswers(answers) {
        const res = super._exportSurveyAnswers(...arguments)
        for (const question of this.dynamicQuestions) {
            for (const option of question.options) {
                let result = false
                if (option.option_name && this[`_evaluate_${question.dynamic_field_type}_condition`]) {
                    result = this[`_evaluate_${question.dynamic_field_type}_condition`](option.option_name)
                }
                if (result) {
                    res.push({
                        survey_id: question.survey_id,
                        question_id: question.question_id,
                        display_name: this._get_multichoice_question_types().includes(question.question_type) ? option.option_id : option.option_name,
                        suggested_answer_id: option.suggested_answer_id,
                        points: option.points,
                    })
                }
            }
        }
        return res
    }
})
