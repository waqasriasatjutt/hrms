/** @odoo-module **/

import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { patch } from "@web/core/utils/patch";
import { reactive} from "@odoo/owl";


patch(TicketScreen.prototype, {

    /* Show the Reorder icon only for completed (paid) orders. */
    shouldShowReorderIcon(order) {
        if (!order) return false;

        const isFinalized = order.finalized === true;

        const isSynced = this.state.filter === "SYNCED";

        return isFinalized && isSynced;
    },

    async onReOrder(order) {
     // Reorder = replay the same order with the same configuration.
        const partner = order.get_partner();
        let currentOrder = this.pos.get_order();
       if (currentOrder?.state !== "draft") {
            currentOrder = this.pos.add_new_order();
        }

        if (currentOrder && partner) {
            currentOrder.set_partner(partner);
        }

       // Re-add each order line using the exact product variant
        for (const line of order.get_orderlines()) {
            const product = line.get_product();
            if (product) {
                await reactive(this.pos).addLineToCurrentOrder(
                    {
                        product_id: product
                    },
                    {
                        quantity: line.get_quantity(),
                        price_unit: line.get_unit_price(),
                        discount: line.get_discount(),
                        customer_note: line.get_customer_note(),
                    },
                    // Do not open configurator on reorder
                    false
                );
            }
        }

        this.pos.showScreen("ProductScreen");
    },
});
