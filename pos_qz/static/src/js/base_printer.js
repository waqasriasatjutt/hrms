/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { renderToElement } from "@web/core/utils/render";

/* ---------------------------------------------------------
   SAFE PRINT COOLDOWN
--------------------------------------------------------- */
let lastPrintTs = 0;
const PRINT_COOLDOWN_MS = 300;

/* ---------------------------------------------------------
   iOS / popup fallback
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
   Wait a short delay for images to load
--------------------------------------------------------- */
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/* ---------------------------------------------------------
   POS PATCH: printReceipt
--------------------------------------------------------- */
patch(PosStore.prototype, {
    async printReceipt({ basic = false, order = this.get_order() } = {}) {
        const now = Date.now();
        if (now - lastPrintTs < PRINT_COOLDOWN_MS) {
            console.warn("🛑 Print blocked (cooldown)");
            return;
        }
        lastPrintTs = now;

        let popupUsed = false;

        try {
            const pos = this;
            order = order || pos.get_order();
            if (!order) return;

            // 1️⃣ Render receipt DOM
            const receiptElement = renderToElement(OrderReceipt, {
                data: pos.orderExportForPrinting(order),
                formatCurrency: this.env.utils.formatCurrency,
                basic_receipt: basic,
            });

            // 2️⃣ Add hidden container so images can load
            const container = document.createElement("div");
            container.style.position = "absolute";
            container.style.left = "-9999px";
            container.appendChild(receiptElement);
            document.body.appendChild(container);

            // 3️⃣ Wait a short delay (e.g., 300ms) for images to load
            await delay(300);

            // 4️⃣ Convert DOM to base64 PNG using html2canvas
            if (typeof html2canvas === "undefined") {
                await new Promise((resolve, reject) => {
                    const s = document.createElement("script");
                    s.src = "https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js";
                    s.onload = resolve;
                    s.onerror = reject;
                    document.head.appendChild(s);
                });
            }

            const canvas = await html2canvas(receiptElement, { scale: 2, useCORS: true, backgroundColor: "#ffffff" });
            const receiptImage = canvas.toDataURL("image/png");

            // 5️⃣ Send sequentially to Python server
            const printersModel = this.models["qz.printer"];
            const printerIds = this.config.qz_receipt_printer_ids || [];
            const ipPrintServer = this.config.central_printer_server_ip || "127.0.0.1";

            for (const rec of printerIds) {
                const printerId = rec?.id || rec;
                const printer = printersModel.get(printerId);
                if (!printer) continue;

                const job_uuid = crypto.randomUUID();

                const payload = {
                    image: receiptImage.replace(/^data:image\/png;base64,/, ""),
                    printer: printer.name,
                    job_type: "receipt",
                    job_uuid: job_uuid,
                };

                const url = `http://${ipPrintServer}:5045/print-image`;
                let sent = false;

                try {
                    const res = await fetch(url, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(payload),
                    });
                    const result = await res.json();

                    if (["queued", "duplicate"].includes(result.status)) {
                        sent = true;
                        console.log(`✅ Queued for printer ${printer.name}`, result.job_id || "");
                    }
                } catch (e) {
                    console.warn("⚠️ Fetch failed, using popup fallback if needed", e);
                }

                if (!sent && !popupUsed) {
                    popupUsed = true;
                    postInNewTab(url, payload);
                }
            }

            document.body.removeChild(container);
            console.log("🧾 All receipt jobs submitted");
        } catch (err) {
            console.error("❌ Receipt print failed", err);
        }
    },
});
