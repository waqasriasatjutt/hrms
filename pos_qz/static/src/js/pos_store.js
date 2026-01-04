// /** @odoo-module **/
//
// import { patch } from "@web/core/utils/patch";
// import { PosStore } from "@point_of_sale/app/store/pos_store";
// import { HWPrinter } from "@point_of_sale/app/printer/hw_printer";
//
// // Custom printer that sends to Python server
// class PythonPrinter extends HWPrinter {
//     async print(Component, props, options = {}) {
//         try {
//             // Render receipt to image (like Odoo does)
//             const receiptImage = await this.env.services.renderer.toJpeg(Component, props, options);
//
//             const printerName = this.config?.qz_receipt_printer || "Default Printer";
//             const response = await fetch("http://127.0.0.1:5045/print-image", {
//                 method: "POST",
//                 headers: { "Content-Type": "application/json" },
//                 body: JSON.stringify({ image: receiptImage.replace(/^data:image\/jpeg;base64,/, ""), printer: printerName }),
//             });
//
//             const result = await response.json();
//             return result.status === "printed" ? { result: true } : { result: false };
//         } catch (e) {
//             console.error("❌ Python print failed", e);
//             return { result: false };
//         }
//     }
//
//     openCashbox() {
//         // Optional: implement if needed
//         return Promise.resolve({ result: true });
//     }
// }
//
// // Patch PosStore to use PythonPrinter
// patch(PosStore.prototype, {
//     async setup(...args) {
//         if (super.setup) await super.setup(...args);
//
//         // Replace printer with PythonPrinter
//         this.printer = new PythonPrinter({ url: "" });
//         this.printer.env = this.env; // necessary to use renderer in print()
//         this.printer.config = this.config; // so printerName works
//     },
// });
