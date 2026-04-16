/**@odoo-module **/
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";
patch(PosOrder.prototype, {

    setReturnReason(returnreason){
        if (returnreason) {
            this.update({ return_reason_id: returnreason });
        } else {
            this.update({ return_reason_id: false });
        }
    }

});