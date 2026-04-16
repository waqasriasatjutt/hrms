/** @odoo-module **/

import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { patch } from "@web/core/utils/patch";
import { formatCurrency } from "@point_of_sale/app/models/utils/currency";

patch(PosOrderline.prototype, {

    displayTaxAmount(){
        if (!this?.config.order_line_tax) {
            return "";
        }

        const productTax = this.get_tax();
        if (productTax !== 0){
            return formatCurrency(this.get_tax(), this.currency);
        }
    },

    getDisplayData() {
        const data = super.getDisplayData();
        return {
            ...data,
            taxAmount: this.displayTaxAmount(),
        };
    },
});
