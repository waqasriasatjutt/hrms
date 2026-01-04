/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosOrder } from "@point_of_sale/app/models/pos_order";

/**
 * Patch PosOrder to include custom_note (General Note) in customer receipt printing
 */
patch(PosOrder.prototype, {
    export_for_printing(baseUrl, headerData) {
        const result = super.export_for_printing(baseUrl, headerData);

        // Add custom_note (General Note) to the receipt data
        result.custom_note = this.custom_note || "";

        // if (!this.last_order_preparation_change) {
        //     this.last_order_preparation_change = {
        //         metadata: {},
        //         lines: {},
        //         generalNote: "",
        //         sittingMode: "Take away", // <-- Default to Take away
        //     };
        // } else {
        //     // If sittingMode is empty or not set, force Take away
        //     this.last_order_preparation_change.sittingMode =
        //         this.last_order_preparation_change.sittingMode || "Take away";
        // }
        //
        // // Also set a convenience property if your POS buttons rely on it
        // this.takeaway = this.last_order_preparation_change.sittingMode === "Take away";

        return result;
    },
});