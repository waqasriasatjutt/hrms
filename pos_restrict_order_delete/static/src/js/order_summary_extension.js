/** @odoo-module */

import { OrderSummary } from "@point_of_sale/app/screens/product_screen/order_summary/order_summary";
import { patch } from "@web/core/utils/patch";

patch(OrderSummary.prototype, {
    /**
     * Override unbookTable to prevent crash on order deletion.
     * We navigate to FloorScreen BEFORE deleting the order to ensure
     * the UI doesn't try to render a deleted order.
     */
    async unbookTable() {
        const order = this.pos.get_order();
        if (order) {
            // Navigate away first to unmount OrderSummary
            this.pos.showScreen("FloorScreen");
            // Then delete the order
            await this.pos.deleteOrders([order]);
        }
    },

    showUnbookButton() {
        const order = this.pos.get_order();
        if (this.pos.selectedTable) {
            return (
                this.pos.config.module_pos_restaurant &&
                !this.pos.models["pos.order"].some(
                    (o) =>
                        o.table_id?.id === this.pos.selectedTable.id &&
                        o.finalized === false &&
                        !o.isBooked
                ) &&
                order && order.lines.length === 0
            );
        }
        return (
            this.pos.config.module_pos_restaurant &&
            order &&
            !order.finalized &&
            order.isBooked &&
            order.lines.length === 0
        );
    }
});
