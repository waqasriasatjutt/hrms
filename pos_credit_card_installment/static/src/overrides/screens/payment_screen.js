/** @odoo-module */

/*
 * Copyright (C) 2025 Axcelere.
 * Licensed under the GPL-3.0 License or later.
 */

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";

patch(PaymentScreen.prototype, {
    setup() {
        super.setup();
        this._autoPaymentPrevented = false;
    },

    onMounted() {
        // Call parent onMounted normally 
        if (super.onMounted) {
            super.onMounted();
        }
    },

    // No need to override payment methods - let the core handle them
});