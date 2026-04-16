/** @odoo-module **/

import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { patch } from "@web/core/utils/patch";

patch(PosOrderline.prototype, {

    setup() {
        super.setup(...arguments);
        this.sequence_number  ||= "";
    },

    getDisplayData() {
        return {
            ...super.getDisplayData(),
            sequence_number : this.sequence_number ,
        };
    },
});

patch(Orderline, {
    props: {
        ...Orderline.props,
        line: {
            ...Orderline.props.line,
            shape: {
                ...Orderline.props.line.shape,
                sequence_number : { type: String, optional: true },
            },
        },
    },
});
