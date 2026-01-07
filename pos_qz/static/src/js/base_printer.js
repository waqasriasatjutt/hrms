/** @odoo-module **/

console.log("🔥 BasePrinter popup-safe patch loaded");

import { patch } from "@web/core/utils/patch";
import { BasePrinter } from "@point_of_sale/app/printer/base_printer";
import { htmlToCanvas } from "@point_of_sale/app/printer/render_service";

/* ---------------------------------------------------------
   Utils
--------------------------------------------------------- */
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function postInNewTab(url, payload) {
    const form = document.createElement("form");
    form.method = "POST";
    form.action = url;
    form.target = "_blank";

    Object.entries(payload).forEach(([k, v]) => {
        const input = document.createElement("input");
        input.type = "hidden";
        input.name = k;
        input.value = typeof v === "string" ? v : JSON.stringify(v);
        form.appendChild(input);
    });

    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);
}

/* ---------------------------------------------------------
   BasePrinter PATCH
--------------------------------------------------------- */
patch(BasePrinter.prototype, {
    async printReceipt(receipt) {
        if (receipt) {
            this.receiptQueue.push(receipt);
        }

        let popupUsed = false;
        let lastResult = { successful: true };

        while (this.receiptQueue.length > 0) {
            const currentReceipt = this.receiptQueue.shift();

            try {
                /* -----------------------------------------
                   Allow DOM + images (logo) to load
                ----------------------------------------- */
                await sleep(60);

                const canvas = await htmlToCanvas(currentReceipt, {
                    addClass: "pos-receipt-print",
                });

                const image = this.processCanvas(canvas);

                const payload = {
                    image: image,
                    printer: this.printer_name || "Default Printer",
                    job_uuid: crypto.randomUUID(),
                };

                const url = `http://${this.ip_print_server}:5045/print-image`;

                let sent = false;

                /* -----------------------------------------
                   1️⃣ PRIMARY: fetch (silent)
                ----------------------------------------- */
                try {
                    await fetch(url, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(payload),
                    });

                    sent = true;
                    console.log("✅ Python print queued");
                } catch (e) {
                    console.warn("⚠️ Fetch blocked, fallback needed", e);
                }

                /* -----------------------------------------
                   2️⃣ FALLBACK: popup (ONCE)
                ----------------------------------------- */
                if (!sent && !popupUsed) {
                    popupUsed = true;
                    console.warn("📤 Opening popup fallback");
                    postInNewTab(url, payload);
                }

                /* -----------------------------------------
                   3️⃣ IoT / Epson (never block POS)
                ----------------------------------------- */
                try {
                    const res = await this._super(currentReceipt);
                    if (res && res.result === false) {
                        console.warn("⚠️ IoT printer rejected job");
                    }
                    lastResult = res || lastResult;
                } catch {
                    console.warn("⚠️ IoT printer crashed, ignored");
                }
            } catch (err) {
                console.error("❌ Receipt failed", err);
                this.receiptQueue.length = 0;
                return this.getActionError();
            }
        }

        return lastResult || { successful: true };
    },
});
