/** @odoo-module **/

import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

patch(PosOrder.prototype, {

    setup() {
        super.setup(...arguments);
        this._recomputeLineSequences();
    },

    _recomputeLineSequences() {
        const lines = this.get_orderlines();
        lines.forEach((line, index) => {
            line.sequence_number  = String(index + 1);
        });
    },


    removeOrderline(lineToRemove) {
        const result = super.removeOrderline(...arguments);
        this._recomputeLineSequences();
        return result;
    },
});
