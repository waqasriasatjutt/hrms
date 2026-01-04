/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosOrder } from "@point_of_sale/app/models/pos_order";

/**
 * Patch PosOrder to include internalNote in customer receipt printing
 * Internal Notes must appear on Customer Receipt (inside order lines)
 */
patch(PosOrder.prototype, {
    export_for_printing(baseUrl, headerData) {
        const result = super.export_for_printing(baseUrl, headerData);

        // Include internalNote in orderlines for receipt display
        // The default export_for_printing omits internalNote, but we need it
        result.orderlines = this.getSortedOrderlines().map((line) => {
            const displayData = line.getDisplayData();
            // Add internalNote back to the display data
            displayData.internalNote = line.getNote() || "";
            return displayData;
        });

        return result;
    },
});