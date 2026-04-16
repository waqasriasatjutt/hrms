/** @odoo-module */

import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";


patch(PosOrder.prototype, {
    setup(vals) {
        super.setup(...arguments);
        this.survey_answers = this.survey_answers || []
    },
});
