/** @odoo-module */

import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

patch(PosOrder.prototype, {

    setup(_defaultObj, options) {
        super.setup(...arguments);
        this.to_invoice = true;
    },

    is_to_invoice() {
        return true;
    },

    set_to_invoice(to_invoice) {
        this.assert_editable();
        this.to_invoice = true;
    },
});
