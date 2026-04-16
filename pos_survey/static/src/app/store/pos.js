/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import {PosSurveyPopup} from "@pos_survey/app/pos_survey_popup/pos_survey_popup";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";


patch(PosStore.prototype, {
    async setup(
        env,
        {
            number_buffer,
            hardware_proxy,
            barcode_reader,
            ui,
            dialog,
            notification,
            printer,
            bus_service,
            pos_data,
            action,
            alert,
        }) {
        this.survey_answers = this.survey_answers || []
        this.answerByOrderUuidCache = {};
        return super.setup(...arguments)
    },

    async _processData(loadedData) {
        super._processData(loadedData)
        this.pos_surveys = loadedData["survey.survey"]
        this.pos_survey_questions = loadedData["survey.question"]
        this.pos_survey_options = loadedData["survey.question.answer"]
        this.session_survey_answers = []
    },

    onSubmitSurvey(answers, timing) {
        if (timing=='order') {
            for (const answer of answers) {
                answer['order_uuid'] = this.get_order().uuid
            }
            this.get_order().survey_answers = answers
        } else {
            for (const answer of answers) {
                answer['session_id'] = this.session.id
            }
            this.survey_answers = answers
        }
    },

    async pay(){
        var surveys = this.models["survey.survey"].filter((survey) =>
            survey.pos_survey_timing == "order"
        );
        if (surveys.length>0) {
            const payload = await makeAwaitable(this.dialog, PosSurveyPopup, {
                pos: this,
                surveys: surveys,
                pos_survey_questions: this.models["survey.question"].getAll(),
                pos_survey_options: this.models["survey.question.answer"].getAll(),
                pos_survey_answers: this.get_order().survey_answers,
                onSubmitSurvey: this.onSubmitSurvey.bind(this),
            });
            if (payload) {
                return super.pay(...arguments)
            }
        } else {
            return super.pay(...arguments)
        }
    },

    async closeSession() {
        var surveys = this.models["survey.survey"].filter((survey) =>
            survey.pos_survey_timing == "session"
        );
        if (surveys.length>0) {
            const payload = await makeAwaitable(this.dialog, PosSurveyPopup, {
                pos: this,
                surveys: surveys,
                pos_survey_questions: this.models["survey.question"].getAll(),
                pos_survey_options: this.models["survey.question.answer"].getAll(),
                pos_survey_answers: this.survey_answers,
                onSubmitSurvey: this.onSubmitSurvey.bind(this),
            });
            if (payload) {
                this.data.call("pos.session", "process_survey", [
                    this.session.id,
                    this.survey_answers,
                ]);
                return super.closeSession(...arguments)
            }
        } else {
            return super.closeSession(...arguments)
        }
        return super.closeSession(...arguments)
    },

    // we need to 'remember' by the order uuid because the order will be deleted
    async preSyncAllOrders(orders) {
        await super.preSyncAllOrders(orders);
        
        for (const order of orders) {
            Object.assign(
                this.answerByOrderUuidCache,
                order.survey_answers.reduce((agg, answer) => {
                    if (answer.order_uuid) {
                        const uuid = answer.order_uuid;
                        if (!agg[uuid]) {
                            agg[uuid] = []; // Initialize as an empty array if not already present
                        }
                        agg[uuid].push({ ...answer }); // Push the answer to the array
                    }
                    return agg;
                }, {})
            );
        }
    },

    // now we reset the survey_answers
    postSyncAllOrders(orders) {
        super.postSyncAllOrders(orders);

        for (const order of orders) {
            if (order.uuid in this.answerByOrderUuidCache) {
                // now will be a good time to send the survey
                if (
                    order.uuid in this.answerByOrderUuidCache && 
                    this.answerByOrderUuidCache[order.uuid].length>0
                ) {
                    order.survey_answers = this.answerByOrderUuidCache[order.uuid]
                    this.data.call("pos.order", "process_survey", [
                        order.id,
                        this.answerByOrderUuidCache[order.uuid],
                    ]);
                }
            }
        }
    },
})
