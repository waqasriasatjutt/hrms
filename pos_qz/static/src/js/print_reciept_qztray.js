/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";

patch(ReceiptScreen.prototype, {
    setup() {
        if (super.setup) super.setup();

        const order = this.pos.get_order();
        // if (order) {
        //     // Auto-print on receipt screen load
        //     this.pos.printReceipt();
        // }
    }
});
