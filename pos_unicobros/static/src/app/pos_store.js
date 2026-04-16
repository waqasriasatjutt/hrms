/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
    // Override
    async setup() {
        await super.setup(...arguments);
        this.data.connectWebSocket("UNICOBROS_LATEST_MESSAGE", (payload) => {
            if (payload.config_id === this.config.id) {
                const pendingLine = this.getPendingPaymentLine("unicobros");
                
                if (pendingLine) {
                    pendingLine.payment_method_id.payment_terminal.handleUnicobrosWebhook(payload);
                }
            }
        });
    },
});
