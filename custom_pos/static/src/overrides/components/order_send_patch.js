/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";

patch(PosStore.prototype, {
    async sendOrderInPreparationUpdateLastChange(order, cancelled = false) {
        if (!order) return;

        // Only run your custom code: mark order as sent to kitchen
        if (!cancelled) {
            order.markAsSentToKitchen();
            console.log("✅ Order marked as sent to kitchen:", order.uid);
        }

        // Call original method for all other behavior
        return this.__proto__.__proto__.sendOrderInPreparationUpdateLastChange.call(this, order, cancelled);
    },
});
