/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosOrder } from "@point_of_sale/app/models/pos_order";

patch(PosOrder.prototype, {
    setup(vals) {
        // Call original setup
        super.setup(vals);

        // Force default order type to TAKEAWAY
        if (!this.last_order_preparation_change) {
            this.last_order_preparation_change = {
                metadata: {},
                lines: {},
                generalNote: "",
                sittingMode: "takeaway",
            };
        } else {
            this.last_order_preparation_change.sittingMode = "takeaway";
        }

        // IMPORTANT: POS UI relies on this flag
        this.takeaway = true;
    },
});
