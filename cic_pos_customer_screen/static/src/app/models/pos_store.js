/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { PartnerList } from "@point_of_sale/app/screens/partner_list/partner_list";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";


patch(PosStore.prototype, {
    async setup() {
        await super.setup(...arguments);
        if (this.config.pos_default_customer_screen){
            this.open_customer_screen()
        }
     },

    async open_customer_screen(){
        const currentOrder = this.get_order();
        if (!currentOrder) {
            return;
        }
        const currentPartner = currentOrder.get_partner();
        const payload = await makeAwaitable(this.dialog, PartnerList, {
            partner: currentPartner,
            getPayload: (newPartner) => currentOrder.set_partner(newPartner),
        });

        if (payload) {
            currentOrder.set_partner(payload);
        }
    },
});
