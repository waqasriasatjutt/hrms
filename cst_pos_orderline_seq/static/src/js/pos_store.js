/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {

    async addLineToOrder() {
        const line = await super.addLineToOrder(...arguments);
        this.selectedOrder?._recomputeLineSequences();
        return line;
    },

});
