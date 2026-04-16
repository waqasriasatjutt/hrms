/** @odoo-module */

import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { patch } from "@web/core/utils/patch";


patch(PosOrderline.prototype, {
    setup() {
    super.setup(...arguments);
    },

    getDisplayData() {
        return {
        ...super.getDisplayData(),
         discount_price: this.get_product().discount_price,
         original_price : this.get_product()._raw.lst_price,
        };
    }
});
    // set product_id in props
    patch(Orderline, {
        props: {
             ...Orderline.props,
        line: {
            ...Orderline.props.line,
        shape: {
            ...Orderline.props.line.shape,
        discount_price: { type: Number, optional: true },
        original_price: { type: Number, optional: true },
            },
            },
        },
    });