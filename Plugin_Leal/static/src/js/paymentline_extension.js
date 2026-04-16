/** @odoo-module **/

import { Payment } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";

// Extender el modelo Paymentline para persistir datos de Leal
// En Odoo 17, Paymentline es una propiedad de la clase Payment
patch(Payment.prototype, {
    // Sobrescribir export_as_JSON para incluir datos de Leal
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
});
