/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { OrderlineNoteButton } from "@point_of_sale/app/screens/product_screen/control_buttons/customer_note_button/customer_note_button";
import { TextInputPopup } from "@point_of_sale/app/utils/input_popups/text_input_popup";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";

// Patch defaultProps
patch(OrderlineNoteButton, {
    defaultProps: {
        label: _t("Printed Note"),
        getter: (orderline) => orderline.get_customer_note(),
        setter: (orderline, note) => orderline.set_customer_note(note),
        class: "",
    },
});

// Patch prototype methods
patch(OrderlineNoteButton.prototype, {
    onClick() {
        // Always use addPrintedNote for our custom button
        return this.props.label === _t("Printed Note")
            ? this.addPrintedNote()
            : this.addLineNotes();
    },

    async addPrintedNote() {
        const selectedOrder = this.pos.get_order();
        if (!selectedOrder) return;

        // Use a custom property instead of general_note to clearly mark it as "Printed Note"
        const selectedNote = selectedOrder.printed_note || "";
        const payload = await this.openTextInput(selectedNote);

        if (typeof payload === "string") {
            // Save under a custom field so orderline/receipt shows "Printed Note"
            selectedOrder.printed_note = payload;

            // Also, make it appear in orderline display
            const line = selectedOrder.get_selected_orderline();
            if (line) {
                line.customer_note = payload; // or use a custom field if needed
                line.trigger('change', { fieldName: 'customer_note' });
            }

            // Trigger reactive update if available
            if (selectedOrder.saveChanges) selectedOrder.saveChanges();
            else if (this.pos.updateSavedOrders) this.pos.updateSavedOrders();
        }

        return { confirmed: typeof payload === "string", inputNote: payload };
    },

    async openTextInput(selectedNote) {
        let buttons = [];
        if (this._isInternalNote() || this.props.label === _t("Printed Note")) {
            buttons = this.pos.models["pos.note"].getAll().map((note) => ({
                label: note.name,
                isSelected: selectedNote.split("\n").includes(note.name),
            }));
        }
        return await makeAwaitable(this.dialog, TextInputPopup, {
            title: _t("Add %s", this.props.label),
            buttons,
            rows: 4,
            startingValue: selectedNote,
        });
    },
});



/** @odoo-module **/

// import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
// import { patch } from "@web/core/utils/patch";

// patch(ControlButtons.prototype, {

//     async clickPrintBillSilent() {
//         try {
//             // --- Step 1: Load QZ Tray ---
//             if (typeof qz === "undefined") {
//                 await this._loadQZTray();
//             }

//             // --- Step 2: Ensure QZ Tray is connected ---
//             if (!qz.websocket.isActive()) {
//                 await qz.websocket.connect();
//                 console.log("✅ QZ Tray connected!");
//             }

//             // --- Step 3: Get available printers ---
//             const printers = await qz.printers.find();
//             console.log("Available printers:", printers);

//             // Pick the first printer for demo purposes
//             const printerName = printers[0] || null;

//             if (!printerName) {
//                 this.showPopup("ErrorPopup", {
//                     title: "No Printer Found",
//                     body: "No printers detected by QZ Tray. Please check QZ Tray setup.",
//                 });
//                 return;
//             }

//             // --- Step 4: Define print data (test print for now) ---
//             const printData = [
//                 {
//                     type: "raw", // send raw ESC/POS text
//                     format: "plain",
//                     data:
//                         "\x1B\x40" + // Initialize printer
//                         "     Odoo POS Test Print\n" +
//                         "-----------------------------\n" +
//                         "Hello from your Odoo 18 POS!\n" +
//                         "This is a sample QZ Tray print.\n" +
//                         "-----------------------------\n" +
//                         "\x1D\x56\x42\x00", // Cut paper
//                 },
//             ];

//             // --- Step 5: Configure printer ---
//             const config = qz.configs.create(printerName);

//             // --- Step 6: Send print job ---
//             await qz.print(config, printData);
//             console.log("✅ Print job sent successfully!");

//         } catch (error) {
//             console.error("❌ QZ Tray print error:", error);
//             this.showPopup("ErrorPopup", {
//                 title: "Print Error",
//                 body: "Error sending print job: " + error.message,
//             });
//         }
//     },

//     async _loadQZTray() {
//         return new Promise((resolve, reject) => {
//             const script = document.createElement("script");
//             script.src = "https://cdn.jsdelivr.net/npm/qz-tray/qz-tray.js";
//             script.onload = resolve;
//             script.onerror = reject;
//             document.head.appendChild(script);
//         });
//     },
// });


// /**@odoo-module **/
// import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
// import { _t } from "@web/core/l10n/translation";
// import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
// import { patch } from "@web/core/utils/patch";
// patch(ControlButtons.prototype, {
//     async VitouPOSPrintSlip() {
//         this.dialog.add(AlertDialog, {
//             title: _t("Print Slip for Kitchen"),
//             body: _t("You can print this slip for kitchen or customer"),
//         });
//     },
// });