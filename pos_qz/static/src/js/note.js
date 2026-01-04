/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";

patch(ControlButtons.prototype, {
    async onClickPrintNote() {
        const order = this.pos.get_order();
        if (!order) return;

        const note = order.general_note || "";
        if (!note.trim()) {
            console.warn("POS: no general note on current order.");
            return;
        }

        const orderType = order.order_type || "Dine In";
        const now = new Date();
        const timeStr = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
        const cashier = this.pos.get_cashier();
        const cashierName = cashier ? cashier.name : "";
        const orderName = order.name || order.uid;

        const escapeHtml = str =>
            String(str || "")
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");

        // ---------- 1️⃣ Build ticket HTML ----------
        const ticketHtml = `
<div class="pos-receipt" style="width:72mm; font-family:monospace; font-size:11px;">
  <div style="font-family:'Courier New', monospace;
    font-size:20px;
    line-height:1.2;
    font-weight:bold;
    white-space:pre;
    color:#000000;
    background:#ffffff;text-align:center;">${escapeHtml(orderType)}</div>
  <div style="font-family:'Courier New', monospace;
    font-size:20px;text-align:center;
    line-height:1.2;
    font-weight:bold;
    white-space:pre;
    color:#000000;
    background:#ffffff;">Time: ${escapeHtml(timeStr)}</div>
  <div style="font-family:'Courier New', monospace;
    font-size:20px;text-align:center;
    line-height:1.2;
    font-weight:bold;
    white-space:pre;
    color:#000000;
    background:#ffffff;">By: ${escapeHtml(cashierName)}</div>
  <div style="font-family:'Courier New', monospace;
    font-size:20px;
    line-height:1.2;text-align:center;
    font-weight:bold;
    white-space:pre;
    color:#000000;
    background:#ffffff;"># ${escapeHtml(orderName)}</div>
  <div style="border-top:1px dashed #000; margin:6px 0;"></div>
  <div style="font-family:'Courier New', monospace;
    font-size:22px;
    line-height:1.2;text-align:center;
    font-weight:bold;
    white-space:pre;
    color:#000000;
    background:#ffffff;"">Printed Note</div>
<div style="
    font-family:'Courier New', monospace;
    font-size:22px;
    line-height:1.2;
    font-weight:normal;
    white-space:pre-wrap;
    word-wrap:break-word;
    color:#000000;
    background:#ffffff;
    width:70mm;
">
    ${escapeHtml(note)}
</div>        `;

        // ---------- 2️⃣ Hidden container for html2canvas ----------
        const container = document.createElement("div");
        container.style.position = "absolute";
        container.style.left = "-9999px";

        const wrapper = document.createElement("div");
        wrapper.style.width = "72mm";
        wrapper.style.fontFamily = "Courier New, monospace";
        wrapper.style.fontSize = "14px";   // or 16px for better visibility
        wrapper.style.lineHeight = "1.2";  // slight spacing for clarity
        wrapper.style.background = "#ffffff";
        wrapper.innerHTML = ticketHtml;
        wrapper.style.width = "288px";
        container.appendChild(wrapper);
        document.body.appendChild(container);

        // ---------- 3️⃣ Load html2canvas if missing ----------
        if (typeof html2canvas === "undefined") {
            await new Promise((resolve, reject) => {
                const s = document.createElement("script");
                s.src = "https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js";
                s.onload = resolve;
                s.onerror = reject;
                document.head.appendChild(s);
            });
        }

        // ---------- 4️⃣ Convert to canvas ----------
        const canvas = await html2canvas(wrapper, {
            scale: 3,
            backgroundColor: "#ffffff",
            useCORS: true,
        });

        const image = canvas.toDataURL("image/png").replace(/^data:image\/png;base64,/, "");
        const printerName = this.pos.config.qz_kitchen_printer || "Default Printer";

        // ---------- 5️⃣ Send to Python Print Server ----------
        try {
            const response = await fetch("http://127.0.0.1:5045/print-image", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    image,
                    printer: printerName,
                }),
            });

            const result = await response.json();
            if (result.status === "printed") {
                this.notification.add(
                    `Printed via local server (${result.printer})`,
                    { type: "success" }
                );
                document.body.removeChild(container);
                return;
            }
            throw new Error(result.error || "Server print failed");

        } catch (err) {
            console.warn("❌ Local print server failed, fallback to QZ Tray/browser", err);
        }

        // ---------- 6️⃣ Fallback to QZ Tray ----------
        try {
            const printerName = this.pos.config.qz_report_printer || "Default Printer";
            if (typeof qz === "undefined") {
                await new Promise((resolve, reject) => {
                    const script = document.createElement("script");
                    script.src = "https://cdn.jsdelivr.net/npm/qz-tray/qz-tray.js";
                    script.onload = resolve;
                    script.onerror = reject;
                    document.head.appendChild(script);
                });
            }
            if (!qz.websocket.isActive()) await qz.websocket.connect();

            const config = qz.configs.create(printerName);
            const printData = [{ type: "image", format: "base64", data: image }];
            await qz.print(config, printData);

            this.notification.add(`Printed via QZ Tray (${printerName})`, { type: "success" });
            document.body.removeChild(container);
            return;
        } catch (err) {
            console.warn("❌ QZ Tray print failed, fallback to browser print", err);
        }

        // ---------- 7️⃣ Browser fallback ----------
        const win = window.open("", "_blank");
        win.document.write(`<html><body><img src="data:image/png;base64,${image}" /></body></html>`);
        win.document.close();
        setTimeout(() => win.print(), 100);

        document.body.removeChild(container);
    },
});
