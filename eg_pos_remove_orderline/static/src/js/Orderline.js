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
         line_id: this.id,
        };
    }
});
patch(Orderline, {
    props: {
         ...Orderline.props,
    line: {
        ...Orderline.props.line,
    shape: {
        ...Orderline.props.line.shape,
    line_id: { type: [String, Number], optional: true },
        },
        },
    },
});

patch(Orderline.prototype, {
    async removeOrderline(line_id) {
        var order = self.posmodel.get_order();
        self.posmodel.get_order().get_orderlines().forEach(function(orderline) {
            if (orderline.id === line_id) {
                order.removeOrderline(orderline);
            }
        });
    }
});