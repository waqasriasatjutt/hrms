/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { changesToOrder } from "@point_of_sale/app/models/utils/order_change";

/**
 * Patch to ensure kitchen paper shows variants in selection order
 * Patches both getPrintingChanges and getRenderedReceipt to sort attribute_value_ids by selection order
 */
patch(PosStore.prototype, {
    /**
     * Override getPrintingChanges to sort attributes in lines by selection order
     */
    getPrintingChanges(order, diningModeUpdate) {
        const result = super.getPrintingChanges(order, diningModeUpdate);
        
        // Sort attributes in each changed line by selection order and add customer notes
        if (result.changedlines && result.changedlines.length > 0) {
            result.changedlines = result.changedlines.map(line => {
                // Find the original orderline
                const orderline = order.get_orderlines().find(l => l.uuid === line.uuid);
                
                // Add customer note to line if it exists
                if (orderline) {
                    const customerNote = orderline.get_customer_note();
                    if (customerNote && customerNote.trim()) {
                        line.customerNote = customerNote;
                    }
                }
                
                // Sort attributes by selection order
                if (line.attribute_value_ids && line.attribute_value_ids.length > 0 && orderline) {
                    if (orderline._attributeSelectionOrder && orderline._attributeSelectionOrder.length > 0) {
                        const selectionOrder = orderline._attributeSelectionOrder;
                        const sortedAttrs = [...line.attribute_value_ids].sort((a, b) => {
                            const orderA = selectionOrder.indexOf(a.id);
                            const orderB = selectionOrder.indexOf(b.id);
                            if (orderA === -1 && orderB === -1) return 0;
                            if (orderA === -1) return 1;
                            if (orderB === -1) return -1;
                            return orderA - orderB;
                        });
                        line.attribute_value_ids = sortedAttrs;
                    }
                }
                
                return line;
            });
        }
        
        return result;
    },
    
    /**
     * Override to sort attributes in kitchen paper lines
     */
    async getRenderedReceipt(order, title, lines, fullReceipt = false, diningModeUpdate) {
        // Sort attributes in each line by selection order
        if (lines && lines.length > 0) {
            lines = lines.map(line => {
                if (line.attribute_value_ids && line.attribute_value_ids.length > 0) {
                    // Find the original orderline to get selection order
                    const orderline = order.get_orderlines().find(l => l.uuid === line.uuid);
                    if (orderline && orderline._attributeSelectionOrder && orderline._attributeSelectionOrder.length > 0) {
                        const selectionOrder = orderline._attributeSelectionOrder;
                        const sortedAttrs = [...line.attribute_value_ids].sort((a, b) => {
                            const orderA = selectionOrder.indexOf(a.id);
                            const orderB = selectionOrder.indexOf(b.id);
                            if (orderA === -1 && orderB === -1) return 0;
                            if (orderA === -1) return 1;
                            if (orderB === -1) return -1;
                            return orderA - orderB;
                        });
                        return { ...line, attribute_value_ids: sortedAttrs };
                    }
                }
                return line;
            });
        }
        
        return super.getRenderedReceipt(order, title, lines, fullReceipt, diningModeUpdate);
    },
});