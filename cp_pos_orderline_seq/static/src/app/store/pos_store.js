/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {

	async addLineToOrder(vals, order, opts = {}, configure = true) {
	    var line = await super.addLineToOrder(...arguments);
	    const lines = this.selectedOrder.get_orderlines();
        lines.forEach((line, index) => {
            let sequence = index + 1;
            line.sequence = sequence.toString();
        });
        return line;
	}

});