/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";


patch(PosStore.prototype, {
async _save_to_server(orders, options) {
        if(orders.length > 0){
            for (let i = 0, len = orders[0].data.statement_ids.length; i < len; i++){
                if (this.orders[0].paymentlines[i]){
                    if(this.orders[0].paymentlines[i].converted_currency){
                        orders[0].data.statement_ids[i][2].currency_amount = this.orders[0].paymentlines[i].converted_currency.amount
                        orders[0].data.statement_ids[i][2].payment_currency = this.orders[0].paymentlines[i].converted_currency.name
                    }else{
                        orders[0].data.statement_ids[i][2].currency_amount = ""
                        orders[0].data.statement_ids[i][2].payment_currency = ""
                    }
                }
            }
        }
        return await super._save_to_server(...arguments)
    }
})
