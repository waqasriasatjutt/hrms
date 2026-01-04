/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";

/**
 * Fix for pos_qz module's onClickPrintNote to ensure document is available
 * This prevents "Cannot read properties of null (reading 'document')" error
 */
patch(ControlButtons.prototype, {
    async onClickPrintNote() {
        // Ensure document is available
        if (typeof document === 'undefined' || document === null) {
            console.error("onClickPrintNote: document is not available");
            this.notification?.add("Print functionality is not available in this context.", { type: "danger" });
            return;
        }
        
        // Call the original method if it exists (from pos_qz module)
        // If pos_qz module is not loaded, this will be undefined
        if (super.onClickPrintNote) {
            return super.onClickPrintNote();
        }
        
        // Fallback: if pos_qz is not loaded, show a message
        const order = this.pos?.get_order();
        if (!order) {
            this.notification?.add("No order available to print.", { type: "warning" });
            return;
        }
        
        const note = order.general_note || "";
        if (!note.trim()) {
            this.notification?.add("No note available to print.", { type: "warning" });
            return;
        }
        
        // Basic print fallback
        try {
            const printWindow = window.open("", "_blank", "width=500,height=700");
            if (!printWindow || !printWindow.document) {
                throw new Error("Could not open print window");
            }
            
            printWindow.document.write(`
                <html>
                    <head>
                        <meta charset="UTF-8">
                        <title>Order Note</title>
                        <style>
                            body { font-family: 'Courier New', monospace; font-size: 11px; margin: 0; padding: 10px; }
                            .note { white-space: pre-wrap; word-wrap: break-word; }
                        </style>
                    </head>
                    <body>
                        <div class="note">${note.replace(/</g, "&lt;").replace(/>/g, "&gt;")}</div>
                    </body>
                </html>
            `);
            printWindow.document.close();
            setTimeout(() => printWindow.print(), 100);
        } catch (error) {
            console.error("Print note error:", error);
            this.notification?.add("Failed to print note: " + error.message, { type: "danger" });
        }
    },
});