/** @odoo-module */

/*
 * Copyright (C) 2025 Axcelere.
 * Licensed under the GPL-3.0 License or later.
 */

import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

patch(PosOrder.prototype, {
    //@override
    setup(_defaultObj, options) {
        super.setup(...arguments);
        this.access_token_payment = this.access_token_payment || null;
    },

    //@override
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.access_token_payment = this.access_token_payment;
        return json;
    },

    //@override
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.access_token_payment = json.access_token_payment;
    },
});
