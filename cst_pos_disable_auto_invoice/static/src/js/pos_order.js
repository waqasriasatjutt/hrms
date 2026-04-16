/** @odoo-module */

import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";
import { useState } from "@odoo/owl";

patch(PosOrder.prototype, {
    set_partner(partner) {
        super.set_partner(partner);
        if (this.config?.auto_invoice_check && partner && !this.uiState?.locked)
        {
            this.set_to_invoice(true);
        }
    },
});
