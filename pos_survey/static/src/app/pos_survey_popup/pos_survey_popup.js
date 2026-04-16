/** @odoo-module */

// import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { Dialog } from "@web/core/dialog/dialog";
import { useState, useRef, Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { usePos } from "@point_of_sale/app/store/pos_hook";


export class PosSurveyPopup extends Component {
    static components = { Dialog };
    static template = "pos_survey.PosSurveyPopup";

    setup() {
        super.setup(...arguments);
        this.dialog = useService("dialog");
        // frontend facing data
        this.state = useState({
            survey: null,
            validationErrors: {},
        });
        this.pos = usePos()

        this.currentSurveyIndex = 0;
        this.surveyData = []; // acts like a local db. TODO: this is redundant
        this.inputRef = useRef("root"); 
        this.loadSurvey();  // Load the survey data
    }

    async loadSurvey() {
        this.surveyData = await this.buildSurveyData(
            this.props.surveys,
            this.props.pos_survey_questions,
            this.props.pos_survey_options,
            this.props.pos_survey_answers,
        );
        this.state.survey = this.surveyData[this.currentSurveyIndex]
    }

    buildSurveyData(surveys, survey_questions, survey_options, survey_answers) {
        return surveys.map(survey => {
            const answers = {};
            survey_answers
                .filter(answer => answer.survey_id === survey.id)
                .forEach(answer => {
                    answers[answer.question_id] = {
                        display_name: answer.display_name,
                        suggested_answer_id: answer.suggested_answer_id,
                    };
                });

            const questions = survey_questions
                .filter(question => question.survey_id.id === survey.id)
                .map(question => {
    
                    const options = survey_options
                        .filter(option => option.question_id.id === question.id)
                        .map(option => ({
                            option_name: option.value,
                            option_id: option.id,
                            points: option.answer_score,
                        }));
    
                    // If `first_option` should always be added, add it here
                    options.unshift({ option_name: '', option_id: false });

                    return {
                        question_name: question.title,
                        question_type: question.question_type,
                        question_answer_score: question.answer_score,
                        question_placeholder: question.question_placeholder,
                        question_answer_numerical_box: question.answer_numerical_box,
                        constr_mandatory: question.constr_mandatory,
                        question_id: question.id,
                        options: options,
                    };
                });
            return {
                survey_name: survey.title,
                survey_id: survey.id,
                survey_timing: survey.pos_survey_timing,
                questions: questions,
                answers: answers,
            };
        });
    }

    nextSurvey() {
        // load new data
        this.currentSurveyIndex += 1;
        this.state = {
            survey: this.surveyData[this.currentSurveyIndex],
            validationErrors: {},
        };
    }
    
    saveSurvey() {
        this.surveyData[this.currentSurveyIndex].answers = this.state.survey.answers;
        if (typeof this.props.onSubmitSurvey === "function") {
            this.props.onSubmitSurvey(this._exportSurveyAnswers(), this.surveyData[this.currentSurveyIndex].survey_timing);
        }
    }
    
    async confirm() {
        await this.validateSurvey()
        if (Object.keys(this.state.validationErrors).length === 0) {
            this.saveSurvey()
            if (this.surveyData.length > this.currentSurveyIndex + 1) {
                this.nextSurvey()
                return;
            }
            this.props.getPayload(this._exportSurveyAnswers())
            this.props.close();
        }
    }
    
    cancel() {
        this.saveSurvey()
        this.props.close();
    }

    validateSurvey() {
        const { survey } = this.state;
        const formElements = this.inputRef.el.querySelectorAll("input, select, textarea");
    
        for (const element of formElements) {
            const questionId = element.getAttribute("data-question-id");
            const question = this.state.survey.questions.filter(question => question.question_id == questionId)[0]
            const value = element.value;
            if (questionId && value != '') {
                delete this.state.validationErrors[questionId]
                
                // save answer
                const questionType = element.tagName.toLowerCase() === "select" ? "simple_choice" : "other";
                const optionId = questionType === "simple_choice" ?
                    element.options[element.selectedIndex].value :
                    false;
                let total_points = 0
                if (question && question.options) {
                    for (const option of question.options) {
                        if (option.option_id == optionId){
                            total_points += option.points
                        }
                    }
                } else if (question && question.question_type=='numerical_box') {
                    if (question.question_answer_numerical_box == value) {
                        total_points += question.question_answer_score
                    }
                }
                survey.answers[questionId] = {
                    display_name: value,
                    suggested_answer_id: optionId,
                    survey_id: survey.survey_id,
                    points: total_points,
                };

            } else if (value == '') {
                if (question.constr_mandatory) {
                    const errors = this.state.validationErrors
                    errors[questionId] = 'This field is required'
                }
            }
        };
    }

    _exportSurveyAnswers() {
        const data=[]
        for (const survey of this.surveyData) {
            Object.entries(survey.answers).forEach(([key, value]) => {
                data.push({
                    survey_id: survey.survey_id,
                    question_id: key,
                    display_name: value.display_name,
                    suggested_answer_id: value.suggested_answer_id,
                    points: value.points,
                })
            });
        }
        return data
    }
}
