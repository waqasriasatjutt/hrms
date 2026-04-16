/** @odoo-module */

import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";
import { OrderWidget } from "@point_of_sale/app/generic_components/order_widget/order_widget";
import { useState } from "@odoo/owl";


patch(OrderWidget, {
    props: {
        ...OrderWidget.props,
        itemCount: { type: Number, optional: true },
        totalQuantity: { type: Number, optional: true },
    },
});

patch(PosOrder.prototype, {
    get itemCount(){
       return this.lines?.length
    },

    get totalQuantity(){
       return this.lines?.reduce((sum, line) => sum + line.get_quantity(), 0);
    },
    
    export_for_printing(baseUrl, headerData) {
        const result = super.export_for_printing(...arguments);

        return {
            ...result,
            itemCount: this.itemCount,
            totalQuantity: this.totalQuantity,
        };
    },
});