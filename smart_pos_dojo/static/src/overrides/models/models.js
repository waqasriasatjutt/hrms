/** @odoo-module */
import { register_payment_method } from "@point_of_sale/app/store/pos_store";
import { PaymentDojo } from "@smart_pos_dojo/app/payment_dojo";
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";


register_payment_method("dojo", PaymentDojo);


patch(PosOrder.prototype, {
    setup(vals) {
        super.setup(...arguments);
        this.dojo_transaction_ids = vals.dojo_transaction_ids || [];
        this.payment_status = vals.payment_status || '';
    },

    set_dojo_transaction: function(dojo_transaction_ids){
        this.dojo_transaction_data = JSON.stringify(dojo_transaction_ids);;
    },
    get_dojo_transaction: function(){
        return this.dojo_transaction_ids;
    },
    get_payment_type: function(){
        return this.payment_type;
    },
    set_payment_status: function(status){
        this.payment_status = status;
    },
});
