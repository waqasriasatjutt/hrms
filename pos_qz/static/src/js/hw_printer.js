// /** @odoo-module **/

// import { patch } from "@web/core/utils/patch";
// import { HWPrinter } from "@point_of_sale/app/printer/hw_printer";

// patch(HWPrinter.prototype, {
//     setup(params) {
//         // ✅ ALWAYS forward params
//         // this._super(...arguments);

//         // ✅ now safe
//         super.setup(...arguments);
//         this.url = params.url;        
//         this.printer_name = params?.printer_name || null;
//     },

//     sendAction(data) {
//         const payload = { ...data };

//         if (this.printer_name) {
//             payload.printer_name = this.printer_name;
//         }

//         return this._super(payload);
//     },
// });
