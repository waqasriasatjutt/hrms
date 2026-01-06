/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { renderToElement } from "@web/core/utils/render";
import { printGeneralNoteImage } from "./note_printer";
import { changesToOrder, getOrderChanges } from "@point_of_sale/app/models/utils/order_change";
import { _t } from "@web/core/l10n/translation";
import { htmlToCanvas } from "@point_of_sale/app/printer/render_service";
import {
    deduceUrl,
    lte,
    random5Chars,
    uuidv4,
    computeProductPricelistCache,
} from "@point_of_sale/utils";
import { Reactive } from "@web/core/utils/reactive";
import { HWPrinter } from "@point_of_sale/app/printer/hw_printer";

patch(PosStore.prototype, {

    async processCanvas(canvas) {
        return canvas.toDataURL("image/jpeg").replace("data:image/jpeg;base64,", "");
    },
create_printer(config) {
    const url = deduceUrl(config.proxy_ip || "");
    return new HWPrinter({
        url,
        printer_name: config.name,   // ✅ EXPLICIT
        printer_name: config.name,   // ✅ EXPLICIT
        ip_print_server: this.config.central_printer_server_ip || "127.0.0.1",



    });
},


});


// /** @odoo-module **/

// import { patch } from "@web/core/utils/patch";
// import { PosStore } from "@point_of_sale/app/store/pos_store";
// import { renderToElement } from "@web/core/utils/render";
// import { printGeneralNoteImage } from "./note_printer";
// import { changesToOrder, getOrderChanges } from "@point_of_sale/app/models/utils/order_change";
// import { _t } from "@web/core/l10n/translation";
// import { htmlToCanvas } from "@point_of_sale/app/printer/render_service";

// patch(PosStore.prototype, {

//     async processCanvas(canvas) {
//         return canvas.toDataURL("image/jpeg").replace("data:image/jpeg;base64,", "");
//     },


//     async sendOrderInPreparation(order, cancelled = false) {
//         let isPrinted = false;
//                 const orderChange = changesToOrder(
//                     order,
//                     false,
//                     this.orderPreparationCategories,
//                     cancelled
//                 );
//                 isPrinted = await this.printChanges(order, orderChange);
//         if (this.printers_category_ids_set.size) {
//             try {
//                 const orderChange = changesToOrder(
//                     order,
//                     false,
//                     this.orderPreparationCategories,
//                     cancelled
//                 );
//                 isPrinted = await this.printChanges(order, orderChange);
//             } catch (e) {
//                 console.info("Failed in printing the changes in the order", e);
//             }
//         }

//         order.updateLastOrderChange();
//         // Ensure that other devices are aware of the changes
//         // Otherwise several devices can print the same changes
//         // We need to check if a preparation display is configured to avoid unnecessary sync
//         if (isPrinted && !this.config["<-pos_preparation_display.display.pos_config_ids"]?.length) {
//             await this.syncAllOrders({ orders: [order] });
//         }
//     },

//     async printChanges(order, orderChange) {
//         let isPrinted = false;
//         const unsuccedPrints = [];
//         const isPartOfCombo = (line) =>
//             line.isCombo || this.models["product.product"].get(line.product_id).type == "combo";
//         const comboChanges = orderChange.new.filter(isPartOfCombo);
//         const normalChanges = orderChange.new.filter((line) => !isPartOfCombo(line));
//         normalChanges.sort((a, b) => {
//             const sequenceA = a.pos_categ_sequence;
//             const sequenceB = b.pos_categ_sequence;
//             if (sequenceA === 0 && sequenceB === 0) {
//                 return a.pos_categ_id - b.pos_categ_id;
//             }

//             return sequenceA - sequenceB;
//         });
//         orderChange.new = [...comboChanges, ...normalChanges];
//         const diningModeUpdate = orderChange.modeUpdate;

//         const receiptEl = await this.getRenderedReceipt(
//             order,
//             "New",
//             orderChange.new,
//             true,
//             diningModeUpdate
//         );

// // Convert to image
// // -------------------------------
// // Convert receiptEl to image using html2canvas
// // -------------------------------
// // const container = document.createElement("div");
// // container.style.position = "absolute";
// // container.style.left = "-9999px";

// // const wrapper = document.createElement("div");
// // wrapper.style.width = "288px";  // same as your second snippet
// // wrapper.appendChild(receiptEl);

// // container.appendChild(wrapper);
// // document.body.appendChild(container);


// // container.appendChild(receiptEl);
// // document.body.appendChild(container);

// // Load html2canvas if not already loaded
// // if (typeof html2canvas === "undefined") {
// //     await new Promise((resolve, reject) => {
// //         const s = document.createElement("script");
// //         s.src = "https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js";
// //         s.onload = resolve;
// //         s.onerror = reject;
// //         document.head.appendChild(s);
// //     });
// // }

// // const canvas = await html2canvas(receiptEl, {
// //     scale: 3,
// //     backgroundColor: "#ffffff",
// // });

// // const receiptImage = canvas
// //         .toDataURL("image/png")
// //         .replace(/^data:image\/png;base64,/, "");

// // // Remove from DOM
// // document.body.removeChild(container);

//             let receiptImage = await this.processCanvas(
//                 await htmlToCanvas(receiptEl, {
//                     addClass: "pos-receipt-print",
//                 })
//             );


//             if (receiptImage) {

// // const printers = this.models["qz.printer"];
// const printers = this.models["qz.printer"];
// const kitchenIds = this.config.qz_kitchen_printer_ids || [];

// // If Many2many is returned as objects like [{id: 1}, {id: 2}]
// for (const kitchen of kitchenIds) {
//     const printerId = kitchen?.id || kitchen; // support both {id: 1} or just 1
//     const printer = printers?.get(printerId);

//     if (printer) {
//         console.log("🍳 Kitchen Printer:", printer.id, printer.name);
//         const printerName = printer.name;
//     const ip_print_server = this.config.central_printer_server_ip || "127.0.0.1"
//     console.log("🎯 Sending print to:", ip_print_server);

//     const response = await fetch("http://"+ip_print_server+":5045/print-image", {
//                     method: "POST",
//                     headers: { "Content-Type": "application/json" },
//                     body: JSON.stringify({
//                         image: receiptImage,
//                         printer: printerName,
//                     }),
//                 });

//                 const result = await response.json();
//                 if (result.status !== "printed") {
//                     throw new Error(result.error || "Kitchen receipt print failed");
//                 }

//                 console.log(`✅ Kitcccchen receipt printed via Python (${result.printer})`);

//                         try {
//             // SECOND PRINT: GENERAL NOTE
//             await printGeneralNoteImage({
//                 pos: this,
//                 order,
//                 printerName: printerName,
//             });
//         } catch (err) {
//             console.error("❌ Auto general note print failed:", err);
//         }

//         // send to server or print here
//     } else {
//         console.warn("❌ Printer not found for ID:", printerId);
//     }
// }

//     // ✅ Send printerName to your server
//     // await this.sendToServer(printerName, data);

//     // 👉 send to server using printerName
//     // sendPrintToServer(printerName, data);

//                 // const printerName = this.config.qz_kitchen_printer || "Default Printer";
//                 // const response = await fetch("http://127.0.0.1:5045/print-image", {
//                 //     method: "POST",
//                 //     headers: { "Content-Type": "application/json" },
//                 //     body: JSON.stringify({
//                 //         image: receiptImage,
//                 //         printer: printerName,
//                 //     }),
//                 // });

//                 // const result = await response.json();
//                 // if (result.status !== "printed") {
//                 //     throw new Error(result.error || "Kitchen receipt print failed");
//                 // }

//                 // console.log(`✅ Kitcccchen receipt printed via Python (${result.printer})`);
// // isPrinted= true;
//             }

//         // try {
//         //     // SECOND PRINT: GENERAL NOTE
//         //     await printGeneralNoteImage({
//         //         pos: this,
//         //         order,
//         //         printerName: this.config.qz_kitchen_printer || "Default Printer",
//         //     });
//         // } catch (err) {
//         //     console.error("❌ Auto general note print failed:", err);
//         // }

    
//         // for (const printer of this.unwatched.printers) {
//         //     const changes = this._getPrintingCategoriesChanges(
//         //         printer.config.product_categories_ids,
//         //         orderChange
//         //     );
//         //     const anyChangesToPrint = changes.new.length;
//         //     const diningModeUpdate = orderChange.modeUpdate;
//         //     if (diningModeUpdate || anyChangesToPrint) {
//         //         const printed = await this.printReceipts(
//         //             order,
//         //             printer,
//         //             "New",
//         //             changes.new,
//         //             true,
//         //             diningModeUpdate
//         //         );
//         //         changes.new = [];
//         //         if (!printed) {
//         //             unsuccedPrints.push("Detailed Receipt");
//         //         } else {
//         //             isPrinted = true;
//         //         }
//         //     }

//         //     // Print all receipts related to line changes
//         //     const toPrintArray = this.preparePrintingData(order, changes);
//         //     for (const [key, value] of Object.entries(toPrintArray)) {
//         //         const printed = await this.printReceipts(order, printer, key, value, false);
//         //         if (!printed) {
//         //             unsuccedPrints.push(key);
//         //         } else {
//         //             isPrinted = true;
//         //         }
//         //     }
//         //     // Print Order Note if changed
//         //     if (orderChange.generalNote && anyChangesToPrint) {
//         //         const printed = await this.printReceipts(order, printer, "Message", []);
//         //         if (!printed) {
//         //             unsuccedPrints.push("General Message");
//         //         } else {
//         //             isPrinted = true;
//         //         }
//         //     }
//         // }

//         // // printing errors
//         // if (unsuccedPrints.length) {
//         //     const failedReceipts = unsuccedPrints.join(", ");
//         //     this.dialog.add(AlertDialog, {
//         //         title: _t("Printing failed"),
//         //         body: _t("Failed in printing %s changes of the order", failedReceipts),
//         //     });
//         // }

//         return isPrinted;
//     },




// //     async sendOrderInPreparationUpdateLastChange(order, cancelled = false) {
// //         if (!order) return;

// //         if (this.data.network.offline) {
// //             this.data.network.warningTriggered = false;
// //             throw new ConnectionLostError();
// //         }

// //         // 1️⃣ ORIGINAL KITCHEN LOGIC
// //         await this.checkPreparationStateAndSentOrderInPreparation(order, cancelled);

// //         try {
// //             // 2️⃣ DERIVE ORDER CHANGE DATA
// // // const orderChange = order.getLastOrderChange
// // //     ? order.getLastOrderChange()
// // //     : { new: order.lines?.filter(line => !line.cancelled) || [], modeUpdate: false };

// // // const lines = orderChange.new;
// // // const diningModeUpdate = orderChange.modeUpdate || false;
// // // const fullReceipt = true;
// // // const title = cancelled ? "Cancelled Items" : "Order Update";
// // // const changes = this._getPrintingCategoriesChanges(
// // //                 printer.config.product_categories_ids,   
// // //                 orderChange
// // //             );

// // // This is the key: use the store method, NOT renderToElement manually
// // // const receiptEl = await this.getRenderedReceipt(
// // //     order,
// // //     "New",
// // //     changes.new,
// // //     fullReceipt,
// // //     diningModeUpdate
// // // );

// // // // Convert to image
// // // // -------------------------------
// // // // Convert receiptEl to image using html2canvas
// // // // -------------------------------
// // // const container = document.createElement("div");
// // // container.style.position = "absolute";
// // // container.style.left = "-9999px";
// // // container.appendChild(receiptEl);
// // // document.body.appendChild(container);

// // // // Load html2canvas if not already loaded
// // // if (typeof html2canvas === "undefined") {
// // //     await new Promise((resolve, reject) => {
// // //         const s = document.createElement("script");
// // //         s.src = "https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js";
// // //         s.onload = resolve;
// // //         s.onerror = reject;
// // //         document.head.appendChild(s);
// // //     });
// // // }

// // // const canvas = await html2canvas(receiptEl, {
// // //     scale: 3,
// // //     backgroundColor: "#ffffff",
// // // });

// // // const receiptImage = canvas
// // //         .toDataURL("image/png")
// // //         .replace(/^data:image\/png;base64,/, "");

// // // // Remove from DOM
// // // document.body.removeChild(container);

// // //             if (receiptImage) {
// // //                 const printerName = this.config.qz_kitchen_printer || "Default Printer";
// // //                 const response = await fetch("http://127.0.0.1:5045/print-image", {
// // //                     method: "POST",
// // //                     headers: { "Content-Type": "application/json" },
// // //                     body: JSON.stringify({
// // //                         image: receiptImage,
// // //                         printer: printerName,
// // //                     }),
// // //                 });

// // //                 const result = await response.json();
// // //                 if (result.status !== "printed") {
// // //                     throw new Error(result.error || "Kitchen receipt print failed");
// // //                 }

// // //                 console.log(`✅ Kitchen receipt printed via Python (${result.printer})`);
// // //             }

// //             // 6️⃣ GENERAL NOTE PRINT
// //             // if (order.general_note) {
// //             //     const noteEl = await renderToElement("point_of_sale.GeneralNoteReceipt", { note: order.general_note });
// //             //     const noteImage = await this.env.services.renderer.toJpeg(noteEl, {}, { addClass: "pos-receipt-print", style: { width: "58mm", fontFamily: "monospace" } });
// //             //     const printerName = this.config.qz_kitchen_printer || "Default Printer";

// //             //     const response = await fetch("http://127.0.0.1:5045/print-image", {
// //             //         method: "POST",
// //             //         headers: { "Content-Type": "application/json" },
// //             //         body: JSON.stringify({
// //             //             image: noteImage.replace(/^data:image\/jpeg;base64,/, ""),
// //             //             printer: printerName,
// //             //         }),
// //             //     });

// //             //     const result = await response.json();
// //             //     if (result.status !== "printed") {
// //             //         throw new Error(result.error || "General note print failed");
// //             //     }

// //             //     console.log(`✅ General note printed via Python (${result.printer})`);
// //             // }

// //         } catch (err) {
// //             console.error("❌ Kitchen / General Note print error:", err);
// //         }

// //         try {
// //             // SECOND PRINT: GENERAL NOTE
// //             await printGeneralNoteImage({
// //                 pos: this,
// //                 order,
// //                 printerName: this.config.qz_kitchen_printer || "Default Printer",
// //             });
// //         } catch (err) {
// //             console.error("❌ Auto general note print failed:", err);
// //         }
// //     },
// });
