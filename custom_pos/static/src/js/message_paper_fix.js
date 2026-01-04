/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosOrder } from "@point_of_sale/app/models/pos_order";

/**
 * Patch to detect Message Paper (receipt with only generalNote, no orderlines)
 * and mark it so CSS can hide the "Message:" title
 */
patch(PosOrder.prototype, {
    export_for_printing(baseUrl, headerData) {
        const result = super.export_for_printing(baseUrl, headerData);

        // Mark if this is a message-only receipt (for Message Paper)
        // Message Paper has generalNote but no orderlines
        if (result.generalNote && (!result.orderlines || result.orderlines.length === 0)) {
            result.isMessagePaper = true;
        }

        return result;
    },
});

