/** @odoo-module **/

export async function printGeneralNoteImage({
    pos,
    order,
    printerName,
    notification = null,
}) {
    if (!order || !order.general_note || !order.general_note.trim()) {
        console.warn("⛔ No general note to print");
        return;
    }
const orderType = order.takeaway ? "Take away" : "Dine In";
        // const now = new Date();
        // const timeStr = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
        const cashier = pos.get_cashier();
        const cashierName = cashier ? cashier.name : "";
        const orderName = order.name || order.uid;
        const note = order.general_note;

    const escapeHtml = str =>
        String(str || "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");

    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

        // const escapeHtml = str =>
        //     String(str || "")
        //         .replace(/&/g, "&amp;")
        //         .replace(/</g, "&lt;")
        //         .replace(/>/g, "&gt;")
        //         .replace(/"/g, "&quot;")
        //         .replace(/'/g, "&#039;");

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

    // Hidden container
    const container = document.createElement("div");
    container.style.position = "absolute";
    container.style.left = "-9999px";

    const wrapper = document.createElement("div");
    wrapper.style.width = "288px";
    wrapper.innerHTML = ticketHtml;

    container.appendChild(wrapper);
    document.body.appendChild(container);

    // Load html2canvas if needed
    if (typeof html2canvas === "undefined") {
        await new Promise((resolve, reject) => {
            const s = document.createElement("script");
            s.src = "https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js";
            s.onload = resolve;
            s.onerror = reject;
            document.head.appendChild(s);
        });
    }

    const canvas = await html2canvas(wrapper, {
        scale: 3,
        backgroundColor: "#ffffff",
    });

    const image = canvas
        .toDataURL("image/png")
        .replace(/^data:image\/png;base64,/, "");

    document.body.removeChild(container);

    const response = await fetch("http://127.0.0.1:5045/print-image", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            image,
            printer: printerName,
        }),
    });

    const result = await response.json();

    if (result.status !== "printed") {
        throw new Error(result.error || "General note print failed");
    }

    if (notification) {
        notification.add(`Printed Note (${result.printer})`, { type: "success" });
    }

    console.log(`✅ General note printed via Python (${result.printer})`);
}
