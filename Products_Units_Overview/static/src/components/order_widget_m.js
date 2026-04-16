/** @odoo-module */

import { OrderWidget } from "@point_of_sale/app/generic_components/order_widget/order_widget";
import { patch } from "@web/core/utils/patch";

patch(OrderWidget.prototype, {
    get ItemCount(){
        return this.props.lines.length
    },

    get TotalQuantity(){
        var totalQty = 0;
        this.props.lines.forEach((orderLine) => {
            totalQty += orderLine.qty;
        });
        this.qty = totalQty;
        return totalQty;
    }
});

