/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { onMounted, onWillUnmount } from "@odoo/owl";

console.log("✅ POS Invoice Toggle JS loaded!");

patch(PaymentScreen.prototype, {
    setup() {
        super.setup(...arguments);
        const config = this.env.services?.pos?.config || {};

        onMounted(() => {
            console.log("📌 PaymentScreen mounted");

            // Check for checkbox in res_config if setting is enabled
            if (!config.hide_pos_invoice_button) return;

            // remove invoice button
            const removeInvoiceBtn = () => {
                const btn = document.querySelector(".js_invoice");
                if (btn) {
                    btn.remove();
                    console.log("🚫 Invoice button removed");
                }
            };

            // Look for a button with class .js_invoice once found remove immediately
            removeInvoiceBtn();

            // Watch for future re-renders
            const target = document.querySelector(".pos");
            if (target) {
                this._observer = new MutationObserver(removeInvoiceBtn);
                this._observer.observe(target, { childList: true, subtree: true });
                console.log("👀 Observing DOM for invoice button");
            }
        });

        // Clean up observer when screen is closed
        onWillUnmount(() => {
            if (this._observer) {
                this._observer.disconnect();
                console.log("🛑 Stopped observing");
            }
        });
    },
});
