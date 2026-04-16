/** @odoo-module **/
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { patch } from "@web/core/utils/patch";

patch(PosOrderline.prototype, {

    setup() {
        super.setup(...arguments);
        this.sequence = this.sequence || "";
    },

    getDisplayData() {
        return {
            ...super.getDisplayData(),
            sequence: this.sequence,
        };
    },
});