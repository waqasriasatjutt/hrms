/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { Payment } from "@point_of_sale/app/store/models";

patch(Payment.prototype, {
    export_for_printing() {
        const result = super.export_for_printing(...arguments);
        if(this.converted_currency){
            result.converted_currency_amount = this.converted_currency.amount
            result.converted_currency_name = this.converted_currency.name
            result.converted_currency_symbol = this.converted_currency.symbol
            this.currency_amount = this.converted_currency.amount
        }
        return result;
    },
});