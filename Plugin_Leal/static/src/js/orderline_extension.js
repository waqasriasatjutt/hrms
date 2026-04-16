/** @odoo-module **/
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { patch } from "@web/core/utils/patch";

patch(PosOrderline.prototype, {
    setup(options) {
        super.setup(...arguments);
        this.leal_redeem_data = options.leal_redeem_data || {};
    },

    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.leal_redeem_data = this.leal_redeem_data || {};
        return json;
    },

    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.leal_redeem_data = json.leal_redeem_data || {};
    },

    set_leal_redeem_data(data) {
        this.leal_redeem_data = data || {};
    },

    get_leal_redeem_data() {
        return this.leal_redeem_data || {};
    },

    export_for_printing() {
        const result = super.export_for_printing(...arguments);
        result.leal_redeem_data = this.get_leal_redeem_data();
        return result;
    },

    getDisplayData() {
        const result = super.getDisplayData(...arguments);
        // Ocultar la nota interna si contiene información sensible de Leal
        if (result.internalNote && result.internalNote.includes("uid_customer")) {
            result.internalNote = "";
        }
        return result;
    }
});