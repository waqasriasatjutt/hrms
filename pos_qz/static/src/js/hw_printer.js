/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { HWPrinter } from "@point_of_sale/app/printer/hw_printer";

patch(HWPrinter.prototype, {
    setup(params) {
        // ✅ ALWAYS forward params
        // this._super(...arguments);

        // ✅ now safe
        super.setup(...arguments);
        this.url = params.url;        
        this.printer_name = params?.printer_name || null;
        this.ip_print_server = params?.ip_print_server || null;

            },

    sendAction(data) {
        const payload = { ...data };

        if (this.printer_name) {
            payload.printer_name = this.printer_name;
        }
        if (this.ip_print_server) {
            payload.ip_print_server = this.ip_print_server;
        }

        return this._super(payload);
    },
});
