/** @odoo-module */

import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { patch } from "@web/core/utils/patch";

patch(TicketScreen.prototype, {
    /**
     * @override
     * Only show delete button if order is Finalized (Receipt) AND Amount is 0.
     * Otherwise hide it.
     */
    shouldHideDeleteButton(order) {
        // Handle both local PosOrder objects and backend order dicts
        let amount = 0;
        if (typeof order.get_total_with_tax === 'function') {
            amount = order.get_total_with_tax();
        } else if (order.amount_total !== undefined) {
            amount = order.amount_total;
        }

        const isZeroAmount = Math.abs(amount) < 0.000001;
        let isFinalized = false;

        // 1. Try using getStatus() logic or finalized property
        if (order.finalized) {
            isFinalized = true;
        } else if (order.state) {
            // For backend orders
            isFinalized = !['draft', 'cancel'].includes(order.state);
        }

        // Show ONLY if (isFinalized AND isZeroAmount)
        // return true to HIDE
        return !(isFinalized && isZeroAmount);
    }
});
