/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";

patch(PosStore.prototype, {
    async sendOrderInPreparationUpdateLastChange(order, cancelled = false) {
        // 🔹 Call original Odoo method (IMPORTANT)
        // await this._super(order, cancelled);
        const result = super.sendOrderInPreparationUpdateLastChange(order, cancelled = false);

        // 🔹 Your custom logic only
        if (order && !cancelled) {
            order.markAsSentToKitchen();
            console.log("✅ Marked as sent to kitchen:", order.uid);
        }
        return result;
    },
});