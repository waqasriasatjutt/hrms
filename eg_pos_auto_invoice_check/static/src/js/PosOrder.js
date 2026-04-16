/** @odoo-module **/

import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

patch(PosOrder.prototype, {
    setup() {
        super.setup(...arguments);
        if (this.config.allow_auto_invoice_true && !this.finalized) {
            this.set_to_invoice(this.config.allow_auto_invoice_true)
        }
    },
});