/** @odoo-module */
import { Order } from "@point_of_sale/app/store/models";
import {patch} from "@web/core/utils/patch";


patch(Order.prototype, {

    init_from_JSON(json) {
        super.init_from_JSON(json);
        this.converted_currency_total = json.converted_currency_total;
        this.converted_currency_change = json.converted_currency_change;
        this.converted_currency_symbol = json.converted_currency_symbol;

    },

    export_as_JSON(){
        const json = super.export_as_JSON(...arguments);

        if (this.converted_currency_total && this.converted_currency_change && this.converted_currency_symbol){
            json.converted_currency_total = this.converted_currency_total;
            json.converted_currency_change =this.converted_currency_change;
            json.converted_currency_symbol = this.converted_currency_symbol;
        }
        return json;
    },
    export_for_printing() {
        const result = super.export_for_printing(...arguments);
        result.converted_currency_total = this.converted_currency_total;
        result.converted_currency_change = this.converted_currency_change;
        result.converted_currency_symbol = this.converted_currency_symbol;
        return result;
    }
});