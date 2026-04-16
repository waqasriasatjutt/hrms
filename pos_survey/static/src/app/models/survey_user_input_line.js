import { registry } from "@web/core/registry";
import { Base } from "@point_of_sale/app/models/related_models";

const { DateTime } = luxon;

export class SurveyUserInputLine extends Base {
    static pythonModel = "survey.user_input.line";
}

registry.category("pos_available_models").add(SurveyUserInputLine.pythonModel, SurveyUserInputLine);
