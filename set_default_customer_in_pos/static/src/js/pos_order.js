/** @odoo-module */

import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

patch(PosOrder.prototype, {

   setup() {
        super.setup(...arguments);
        if(this.config.default_pos_partner_id && !this.partner_id){
            this.partner_id = this.config.default_pos_partner_id;
        }
    },
    
});

