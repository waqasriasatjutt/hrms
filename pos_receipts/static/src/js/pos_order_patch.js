/* @odoo-module */

import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";
import { formatDate, formatDateTime, serializeDateTime } from "@web/core/l10n/dates";
import { parseUTCString, qrCodeSrc, random5Chars, uuidv4, gte, lt } from "@point_of_sale/utils";

patch(PosOrder.prototype, {
 export_for_printing(baseUrl, headerData) {
        // Call original method first
        const result = super.export_for_printing(baseUrl, headerData);

        // Add date_order into headerData
        result.headerData = {
            ...result.headerData,
            date_order: this.date_order
                ? formatDateTime(parseUTCString(this.date_order))
                : null,

             // 🔹 Add cashier name
            cashier: this.getCashierName ? this.getCashierName() : (this.cashier?.name || ""),
        };





        console.log("📦 Data for receipt:", result);

        return result;
    },


});

















///** @odoo-module **/
//
//import { PosOrder } from "@point_of_sale/app/models/pos_order";
//import { patch } from "@web/core/utils/patch";
//
//patch(PosOrder.prototype, {
//    export_for_printing(baseUrl, headerData) {
//        console.log("✅ export_for_printing patch is active!");
//
//        const data = super.export_for_printing(...arguments);
//
//        console.log("📅 Fetching date_order:", this.date_order);
//
//        // Format the date_order properly
//        if (this.date_order) {
//            const dateObj = new Date(this.date_order);
//            const formattedDate = dateObj.toLocaleString(); // e.g., 9/10/2025, 12:33:52 PM
//            data.date_order = formattedDate;
//        }
//
//
////       // 🔹 Add raw cashier name (avoid "Served by")
////        data.cashier_name = this.cashier?.name || "";
////        console.log("👨‍💼 Cashier raw name:", this.cashier);
////        console.log("✅ Final cashier_name for receipt:", data.cashier_name);
//
//
//        console.log("📦 Data for receipt:", data);
//
//        return data;
//    },
//});
