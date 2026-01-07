/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { handleSaleDetails } from "@point_of_sale/app/navbar/sale_details_button/sale_details_button";
import { renderToElement } from "@web/core/utils/render";

patch(Navbar.prototype, {
    name: "pos_custom_sale_report.Navbar",

    get showSaleDetailsButton() {
        return true;
    },

    async showSaleDetails() {
        // 1️⃣ Get sale details
        const saleDetails = await this.pos.data.call(
            "report.point_of_sale.report_saledetails",
            "get_sale_details",
            [false, false, false, [this.pos.session.id]]
        );

        // 2️⃣ Render SaleDetailsReport template
        const reportHtml = renderToElement("point_of_sale.SaleDetailsReport", {
            ...saleDetails,
            date: new Date().toLocaleString(),
            pos: this.pos,
            formatCurrency: this.pos.env.utils.formatCurrency,
        });

        // 3️⃣ PRIORITY 1: IoT Printer
        if (this.hardwareProxy?.printer) {
            await handleSaleDetails(this.pos, this.hardwareProxy, this.dialog);
            return;
        }

        // 4️⃣ Load html2canvas if missing
        if (typeof html2canvas === "undefined") {
            await new Promise((resolve, reject) => {
                const s = document.createElement("script");
                s.src = "https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js";
                s.onload = resolve;
                s.onerror = reject;
                document.head.appendChild(s);
            });
        }

        // 5️⃣ Hidden container
        const container = document.createElement("div");
        container.style.position = "absolute";
        container.style.left = "-9999px";

        // ✅ THERMAL-OPTIMIZED WRAPPER
        const wrapper = document.createElement("div");
        wrapper.style.width = "70mm";                 // ✅ Correct printable width (58mm paper)
        wrapper.style.padding = "5mm 2mm 0 2mm";      // ✅ Minimal margins
        wrapper.style.boxSizing = "border-box";
        wrapper.style.background = "#ffffff";
        wrapper.style.fontFamily = "monospace";
        wrapper.style.fontSize = "14px";
        wrapper.style.lineHeight = "1.1";

        wrapper.appendChild(reportHtml);
        container.appendChild(wrapper);
        document.body.appendChild(container);

        // ✅ FORCE COMPACT TEXT (important)
        wrapper.querySelectorAll("*").forEach(el => {
            el.style.lineHeight = "1.1";
            el.style.margin = "0";
            el.style.padding = "0";
            el.style.color = "#000";
        });

        // 6️⃣ Convert to canvas (NO ZOOM)
        const canvas = await html2canvas(wrapper, {
            scale: 2    ,                         // ✅ Prevent zoom
            backgroundColor: "#ffffff",
            useCORS: true,
        });

        // ✅ PNG = sharp text for thermal printers
        const image = canvas.toDataURL("image/png");

        // 7️⃣ PRIORITY 2: QZ Tray


const printers = this.pos.models["qz.printer"];

const printer = printers?.get(this.pos.config.qz_report_printer_id?.id);
const ip_print_server = this.pos.config.central_printer_server_ip || "127.0.0.1"

const printerName = printer?.name || "Default Printer";

    console.log("🎯 Sending print to:", ip_print_server);


        // const printerName = this.pos.config.qz_report_printer || "Default Printer";

// 8️⃣ PRIORITY 3: Python Print Server fallback
try {
    const response = await fetch("http://"+ip_print_server+":5045/print-image", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            image: image.replace(/^data:image\/png;base64,/, ""),
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
    console.error("❌ Local print server failed", err);
}


        // try {
        //     if (typeof qz === "undefined") {
        //         await new Promise((resolve, reject) => {
        //             const script = document.createElement("script");
        //             script.src = "https://cdn.jsdelivr.net/npm/qz-tray/qz-tray.js";
        //             script.onload = resolve;
        //             script.onerror = reject;
        //             document.head.appendChild(script);
        //         });
        //     }
        //
        //     if (!qz.websocket.isActive()) {
        //         await qz.websocket.connect();
        //     }
        //
        //     // ✅ Disable auto scaling
        //     const config = qz.configs.create(printerName, {
        //         scaleContent: true,
        //         density: 203,
        //         rasterize: true,
        //     });
        //
        //     const printData = [{
        //         type: "image",
        //         format: "base64",
        //         data: image.replace(/^data:image\/png;base64,/, ""),
        //     }];
        //
        //     await qz.print(config, printData);
        //
        //     this.notification.add(
        //         `Sale Details printed via ${printerName}.`,
        //         { type: "success" }
        //     );
        //
        //     document.body.removeChild(container);
        //     return;
        //
        // } catch (err) {
        //     console.warn("QZ Tray failed, falling back to browser print", err);
        // }

        // 8️⃣ PRIORITY 3: Browser fallback
        const win = window.open("", "_blank");
        win.document.write(`
<html>
<head>
    <title>Sale Details</title>
    <style>
        body { margin:0; padding:0; background:#fff; font-family:monospace; }
        img { width:48mm; display:block; margin:10px auto 0 auto; }
    </style>
</head>
<body>
    <img src="${image}" />
    <script>window.onload = () => window.print();</script>
</body>
</html>
        `);
        win.document.close();

        document.body.removeChild(container);
    },
});
