/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
// import { PosOrder } from "@point_of_sale/models/pos_order/pos_order";

import { PosOrder } from "@point_of_sale/app/models/pos_order";

patch(PosOrder.prototype, {
    getLBPRate() {
        // safe access to config
        return this.config?.dual_currency_rate || 89500;
    },
});
