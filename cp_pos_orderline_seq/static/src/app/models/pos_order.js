/** @odoo-module **/
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

patch(PosOrder.prototype, {
    removeOrderline(lineToRemove) {
        var line = super.removeOrderline(lineToRemove);
        const lines = posmodel.selectedOrder.get_orderlines();
        lines.forEach((line, index) => {
            let sequence = index + 1;
            line.sequence = sequence.toString();
        });
        return line
    }
})