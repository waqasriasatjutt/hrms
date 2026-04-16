/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { OrderWidget } from "@point_of_sale/app/generic_components/order_widget/order_widget";


import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";

import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";

/**
 * Patch PosOrderline to inject productId into receipt data
 */
patch(PosOrderline.prototype, {

    getDisplayData() {
        const data = super.getDisplayData(...arguments);

        return {
            ...data,
            productId: this.product_id?.id || null,
        };
    },

});

Orderline.props.line.shape.productId = {
    type: Number,
    optional: true,
};


patch(OrderWidget.prototype, {

    get totalQty() {
        if (!this.props.lines) return 0;

        let total = 0;

        for (const line of this.props.lines) {

            if (typeof line.qty === "number") {
                total += line.qty;
            }

            else if (typeof line.qty === "string") {
                total += Number(line.qty) || 0;
            }
        }

        return total;
    },

    get totalLines() {
        return this.props.lines?.length || 0;
    },

    get uniqueProducts() {
        if (!this.props.lines) return 0;

        const productIds = new Set();

        for (const line of this.props.lines) {
            if (line.product_id?.id) {
                productIds.add(line.product_id.id);
            }
            else if (line.productId) {
                productIds.add(line.productId);
            }
            else if (line.product_id && typeof line.product_id === "number") {
                productIds.add(line.product_id);
            }
        }

        return productIds.size;
    },
});
