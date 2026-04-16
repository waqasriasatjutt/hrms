/**@odoo-module **/
import { _t } from "@web/core/l10n/translation";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { patch } from "@web/core/utils/patch";
patch(ControlButtons.prototype, {

    async  click() {
        const order = this.pos.get_order();
        console.log("order",order)
        while (order.get_selected_orderline()) {
            order.removeOrderline(order.get_selected_orderline())
        }
    }
});