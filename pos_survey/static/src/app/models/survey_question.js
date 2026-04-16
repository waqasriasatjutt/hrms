import { registry } from "@web/core/registry";
import { Base } from "@point_of_sale/app/models/related_models";

const { DateTime } = luxon;

export class SurveyQuestion extends Base {
    static pythonModel = "survey.question";
}

registry.category("pos_available_models").add(SurveyQuestion.pythonModel, SurveyQuestion);
