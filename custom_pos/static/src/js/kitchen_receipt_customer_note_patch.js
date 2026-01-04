/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { getOrderChanges } from "@point_of_sale/app/models/utils/order_change";

/**
 * Patch to include customer_note in kitchen paper line data
 * We need to modify the getOrderChanges function to include customer_note
 */
// Since getOrderChanges is exported, we'll patch where it's used
// Actually, let's patch the PosStore getPrintingChanges to collect customer notes

import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
    getPrintingChanges(order, diningModeUpdate) {
        const result = super.getPrintingChanges(order, diningModeUpdate);
        
        // Collect all customer notes from orderlines
        const customerNotes = [];
        order.get_orderlines().forEach(line => {
            const customerNote = line.get_customer_note();
            if (customerNote && customerNote.trim()) {
                customerNotes.push({
                    line_uuid: line.uuid,
                    product_name: line.get_full_product_name(),
                    note: customerNote
                });
            }
        });
        
        result.customer_notes = customerNotes;
        
        return result;
    },
});