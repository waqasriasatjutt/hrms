/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

/**
 * Patch PosStore to include custom_note (General Note) in kitchen paper printing
 * Also mark if this is kitchen paper (has orderlines) vs message paper (no orderlines)
 */
patch(PosStore.prototype, {
    getPrintingChanges(order, diningModeUpdate) {
        const result = super.getPrintingChanges(order, diningModeUpdate);
        
        // Add custom_note (General Note) to the changes data
        result.custom_note = order.custom_note || "";
        
        // Mark if this is kitchen paper (has orderlines) or message paper (no orderlines)
        // Kitchen paper has changedlines, message paper doesn't
        result.isKitchenPaper = result.changedlines && result.changedlines.length > 0;
        
        return result;
    },
});