/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";

patch(PosStore.prototype, {
async printReceipt({
        basic = false,
        order = this.get_order(),
        printBillActionTriggered = false,
    } = {}) {
        const pos = this;
        // Wrap raw order in PosOrder instance
        if (order && !order.getCashierName) {
            order = this.get_order(order.uuid) || order;
        }
        order = order || pos.get_order();

        if (!order) {
            console.warn("⛔ No order to print");
            return;
        }

        try {
            // ------------------------------------------------------------------
            // 1️⃣ Render receipt as IMAGE (same quality as QZ)
            // ------------------------------------------------------------------
            const receiptImage = await this.env.services.renderer.toJpeg(
                OrderReceipt,
                {
                    data: pos.orderExportForPrinting(order),
                    formatCurrency: this.env.utils.formatCurrency,
                    basic_receipt: basic,
                },
                {
                    addClass: "pos-receipt-print",
                    style: {
                        width: "58mm",
                        fontFamily: "monospace",
                    },
                }
            );

            if (!receiptImage) {
                console.warn("⛔ Failed to generate receipt image");
                return;
            }

            // ------------------------------------------------------------------
            // 2️⃣ Send image to PYTHON PRINT SERVER
            // ------------------------------------------------------------------
//             const printerName = this.env.services.pos_data.models["qz.printer"]
//     .get(this.config.qz_receipt_printer_id)
//     .name
//  || "Default Printer";



console.log("🧪 POS MODELS:", Object.keys(this.models || {}));

const printerModel = this.models?.["qz.printer"];
console.log("🧪 qz.printer model:", printerModel);

if (!printerModel) {
    console.error("❌ qz.printer model NOT loaded in POS");
} else {
    console.log("✅ qz.printer model LOADED");

    // --------------------------------------------------------
    // 🔍 All printers
    // --------------------------------------------------------
    const allPrinters = printerModel.getAll?.() || [];
    console.log("🖨️ All QZ Printers (count):", allPrinters.length);
    console.table(
        allPrinters.map(p => ({
            id: p.id,
            name: p.name,
        }))
    );

    // --------------------------------------------------------
    // 🔍 Config printer ID
    // --------------------------------------------------------
    console.log(
        "📌 config.qz_receipt_printer_id:",
        this.config.qz_receipt_printer_id?.id,
        typeof this.config.qz_receipt_printer_id?.id
    );

    // --------------------------------------------------------
    // 🔍 Matching printer
    // --------------------------------------------------------
    const selectedPrinter = printerModel.get(
        this.config.qz_receipt_printer_id
    );

    console.log("🎯 Selected printer record:", selectedPrinter);
}


const printers = this.models["qz.printer"];

const printer = printers?.get(this.config.qz_receipt_printer_id?.id);

const printerName = printer?.name || "Default Printer";

const ip_print_server = this.config.central_printer_server_ip || "127.0.0.1"


    console.log("🎯 Sending print to:", ip_print_server);

    const response = await fetch("http://"+ip_print_server+":5045/print-image", {

                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    image: receiptImage.replace(
                        /^data:image\/jpeg;base64,/,
                        ""
                    ),
                    printer: printerName,
                }),
            });

            const result = await response.json();

            if (result.status !== "printed") {
                throw new Error(result.error || "Receipt print failed");
            }

            console.log(
                `✅ Receipt printed via Python (${result.printer})`
            );

        } catch (err) {
            console.error("❌ Receipt print error:", err);
        }
    },
});


// /** @odoo-module **/
//
// import { patch } from "@web/core/utils/patch";
// import { PosStore } from "@point_of_sale/app/store/pos_store";
// import { nextTick } from "@odoo/owl";
// import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
//
// patch(PosStore.prototype, {
//     async printReceipt(order = null, printOptions = {}) {
//         const pos = this;
//         order = order || pos.get_order();
//
//         if (!order) {
//             console.warn("⛔ PosStore.printReceipt: No order to print");
//             return;
//         }
//
//         try {
//             // ------------------------------------------------------------------------------------
//             // 1️⃣ Detect if QZ Tray is running (local websocket test)
//             // ------------------------------------------------------------------------------------
//             const qzRunning = await new Promise((resolve) => {
//                 let done = false;
//                 const ws = new WebSocket("ws://localhost:8182");
//
//                 ws.onerror = () => {
//                     if (!done) resolve(false);
//                     done = true;
//                 };
//                 ws.onopen = () => {
//                     ws.close();
//                     if (!done) resolve(true);
//                     done = true;
//                 };
//
//                 setTimeout(() => {
//                     if (!done) resolve(false);
//                     done = true;
//                 }, 800);
//             });
//
//             if (!qzRunning) {
//                 console.warn("⛔ QZ Tray not running");
//                 return;
//             }
//
//             // ------------------------------------------------------------------------------------
//             // 2️⃣ Load qz-tray.js dynamically if missing
//             // ------------------------------------------------------------------------------------
//             if (typeof qz === "undefined") {
//                 await new Promise((resolve, reject) => {
//                     const s = document.createElement("script");
//                     s.src = "https://cdn.jsdelivr.net/npm/qz-tray/qz-tray.js";
//                     s.onload = resolve;
//                     s.onerror = reject;
//                     document.head.appendChild(s);
//                 });
//             }
//
//             // ------------------------------------------------------------------------------------
//             // 3️⃣ Ensure websocket is connected
//             // ------------------------------------------------------------------------------------
//             if (!qz.websocket.isActive()) {
//                 await qz.websocket.connect();
//             }
//
//             // ------------------------------------------------------------------------------------
//             // 4️⃣ Render receipt as image
//             // ------------------------------------------------------------------------------------
//             const receiptImage = await this.env.services.renderer.toJpeg(
//                 OrderReceipt,
//                 {
//                     data: pos.orderExportForPrinting(order),
//                     formatCurrency: this.env.utils.formatCurrency,
//                     basic_receipt: !!printOptions.basic,
//                 },
//                 { addClass: "pos-receipt-print p-3" }
//             );
//
//             if (!receiptImage) {
//                 console.warn("⛔ Could not generate receipt image");
//                 return;
//             }
//
//             // ------------------------------------------------------------------------------------
//             // 5️⃣ Use POS Config printer (MAIN UPDATE)
//             // ------------------------------------------------------------------------------------
//             // const printerName = this.pos.config.qz_kitchen_printer || "Default Printer";
//             const printerName = this.config.qz_receipt_printer || "Default Printer";
//
//             console.log("📌 Using QZ Tray Printer (Receipt):", printerName);
//
//             const config = qz.configs.create(printerName);
//
//             // ------------------------------------------------------------------------------------
//             // 6️⃣ Prepare print payload
//             // ------------------------------------------------------------------------------------
//             const printData = [{
//                 type: "image",
//                 format: "base64",
//                 data: receiptImage.replace(/^data:image\/jpeg;base64,/, ""),
//             }];
//
//             // ------------------------------------------------------------------------------------
//             // 7️⃣ Print
//             // ------------------------------------------------------------------------------------
//             await qz.print(config, printData);
//             console.log("✅ Receipt printed successfully via QZ");
//
//         } catch (err) {
//             console.error("❌ QZ print error:", err);
//         }
//     },
// });