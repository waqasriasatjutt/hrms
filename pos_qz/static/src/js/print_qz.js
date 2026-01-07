/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";

/* ---------------------------------------------------------
   SAFE PRINT COOLDOWN (avoid accidental double clicks)
--------------------------------------------------------- */
let lastPrintTs = 0;
const PRINT_COOLDOWN_MS = 300; // short enough to allow multiple legitimate clicks

/* ---------------------------------------------------------
   iOS / popup fallback (only once per print action)
--------------------------------------------------------- */
function postInNewTab(url, data) {
    const form = document.createElement("form");
    form.method = "POST";
    form.action = url;
    form.target = "_blank";

    Object.entries(data).forEach(([key, value]) => {
        const input = document.createElement("input");
        input.type = "hidden";
        input.name = key;
        input.value = typeof value === "object" ? JSON.stringify(value) : value;
        form.appendChild(input);
    });

    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);
}

/* ---------------------------------------------------------
   POS PATCH: printReceipt
--------------------------------------------------------- */
patch(PosStore.prototype, {
    async printReceipt({
        basic = false,
        order = this.get_order(),
    } = {}) {
        const now = Date.now();

        // 🔒 SHORT COOLDOWN to prevent accidental double click
        if (now - lastPrintTs < PRINT_COOLDOWN_MS) {
            console.warn("🛑 Print blocked (cooldown)");
            return;
        }
        lastPrintTs = now;

        let popupUsed = false; // ensure only one popup per action

        try {
            const pos = this;

            if (order && !order.getCashierName) {
                order = this.get_order(order.uuid) || order;
            }
            order = order || pos.get_order();
            if (!order) return;

            // 1️⃣ Render receipt to JPEG image
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

            if (!receiptImage) throw new Error("Receipt render failed");

            // 2️⃣ Resolve printers
            const printersModel = this.models["qz.printer"];
            const printerIds = this.config.qz_receipt_printer_ids || [];
            const ipPrintServer = this.config.central_printer_server_ip || "127.0.0.1";

            if (!printersModel || !printerIds.length) {
                throw new Error("No receipt printers configured");
            }

            // 3️⃣ Sequentially send to Python server
            for (const rec of printerIds) {
                const printerId = rec?.id || rec;
                const printer = printersModel.get(printerId);
                if (!printer) continue;

                // Generate a unique job per click (avoids server dedup issues)
                const job_uuid = crypto.randomUUID();

                const payload = {
                    image: receiptImage.replace(/^data:image\/jpeg;base64,/, ""),
                    printer: printer.name,
                    job_type: "receipt",
                    job_uuid: job_uuid,
                };

                const url = `http://${ipPrintServer}:5045/print-image`;
                let sent = false;

                // 🔹 Try fetch first
                try {
                    const res = await fetch(url, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(payload),
                    });

                    const result = await res.json();

                    if (["queued", "duplicate"].includes(result.status)) {
                        sent = true;
                        console.log(
                            `✅ Queued for printer ${printer.name}`,
                            result.job_id || ""
                        );
                    } else {
                        throw new Error(result?.error || "Rejected");
                    }
                } catch (e) {
                    console.warn("⚠️ Fetch failed, fallback will be used if needed", e);
                }

                // 🔹 Only one popup per print action
                if (!sent && !popupUsed) {
                    popupUsed = true;
                    console.warn(`📤 Using popup fallback for printer ${printer.name}`);
                    postInNewTab(url, payload);
                }
            }

            console.log("🧾 All receipt jobs submitted");
        } catch (err) {
            console.error("❌ Receipt print failed", err);
        }
    },
});
