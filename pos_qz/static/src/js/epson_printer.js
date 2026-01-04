// /** @odoo-module **/

// console.log("🔥 pos_qz Epson patch file loaded");

// import { patch } from "@web/core/utils/patch";
// import { EpsonPrinter } from "@pos_epson_printer/app/epson_printer";
// patch(EpsonPrinter.prototype, {
//     async sendPrintingJob(img) {
//         // 1️⃣ Always send to Python
//         try {
//             await fetch("http://127.0.0.1:5045/print-image", {
//                 method: "POST",
//                 headers: { "Content-Type": "application/json" },
//                 body: JSON.stringify({
//                     image: img,
//                     printer: this.printer_name || "Default Printer",
//                 }),
//             });
//         } catch (e) {
//             console.warn("Python print failed", e);
//         }

//         // 2️⃣ Try Epson, but NEVER fail POS
//         try {
//             const res = await this._super(img);

//             // If Epson explicitly failed, ignore it
//             if (!res || res.result === false) {
//                 return { result: true };
//             }

//             return res;
//         } catch (e) {
//             // Epson crashed → still succeed
//             return { result: true };
//         }
//     },
// });
