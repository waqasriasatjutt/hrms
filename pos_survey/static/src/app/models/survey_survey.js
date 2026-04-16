import { registry } from "@web/core/registry";
import { Base } from "@point_of_sale/app/models/related_models";

const { DateTime } = luxon;

export class SurveySurvey extends Base {
    static pythonModel = "survey.survey";
}

registry.category("pos_available_models").add(SurveySurvey.pythonModel, SurveySurvey);
