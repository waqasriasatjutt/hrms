/** @odoo-module **/

console.log("🔥 Base Printer patch file loaded");

import { patch } from "@web/core/utils/patch";
import { BasePrinter } from "@point_of_sale/app/printer/base_printer";
import { htmlToCanvas } from "@point_of_sale/app/printer/render_service";

/* -------------------------------
   POST via new tab (fallback)
-------------------------------- */
function postInNewTab(url, data) {
    const form = document.createElement("form");
    form.method = "POST";
    form.action = url;
    form.target = "_blank";

    Object.keys(data).forEach((key) => {
        const input = document.createElement("input");
        input.type = "hidden";
        input.name = key;
        input.value = typeof data[key] === "object"
            ? JSON.stringify(data[key])
            : data[key];
        form.appendChild(input);
    });

    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);
}

/* -------------------------------
   Patch BasePrinter
-------------------------------- */
patch(BasePrinter.prototype, {
    async printReceipt(receipt) {
        if (receipt) this.receiptQueue.push(receipt);

        while (this.receiptQueue.length > 0) {
            receipt = this.receiptQueue.shift();

            const image = this.processCanvas(
                await htmlToCanvas(receipt, { addClass: "pos-receipt-print" })
            );

            const url = "http://" + this.ip_print_server + ":5045/print-image";
            const payload = {
                image: image,
                printer: this.printer_name || "Default Printer",
            };

            /* -------------------------------
               Try fetch first
            -------------------------------- */
            try {
                await fetch(url, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload),
                });
            } catch (e) {
                console.warn("⚠️ Fetch failed, fallback to new tab POST", e);
                // fallback for iOS / blocked HTTP / mixed content
                postInNewTab(url, payload);
            }

            /* -------------------------------
               2️⃣ Epson / IoT Printer (never fail POS)
            -------------------------------- */
            try {
                const res = await this._super(image);
                if (!res || res.result === false) return { successful: true };
                return res;
            } catch (e) {
                return { successful: true };
            }
        }

        return { successful: true };
    },
});
