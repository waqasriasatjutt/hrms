/** @odoo-module **/ 
console.log("🔥 Base Printer patch file loaded"); 
import { patch } from "@web/core/utils/patch"; 
import { BasePrinter } from "@point_of_sale/app/printer/base_printer"; 
import { _t } from "@web/core/l10n/translation";
import { htmlToCanvas } from "@point_of_sale/app/printer/render_service";
patch(BasePrinter.prototype, {
        async printReceipt(receipt) {
        if (receipt) {
            this.receiptQueue.push(receipt);
        }
        let image, printResult;
        while (this.receiptQueue.length > 0) {
            receipt = this.receiptQueue.shift();
            image = this.processCanvas(
                await htmlToCanvas(receipt, { addClass: "pos-receipt-print" })
            );
            try {

        try {

    console.log("🎯 Sending print to:", this.ip_print_server);


            await fetch("https://"+this.ip_print_server+"/print-image", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    image: image,
                    printer: this.printer_name || "Default Printer",
                }),
            });
        } catch (e) {
            console.warn("Python print failed", e);
        }

        // 2️⃣ Try Epson, but NEVER fail POS
        try {
            const res = await this._super(img);

            // If Epson explicitly failed, ignore it
            if (!res || res.result === false) {
                return { successful: true };
            }

            return res;
        } catch (e) {
            // Epson crashed → still succeed
            return { successful: true };
        }

                // printResult = await this.sendPrintingJob(image);
            } catch {
                // Error in communicating to the IoT box.
                this.receiptQueue.length = 0;
                return this.getActionError();
            }
            // rpc call is okay but printing failed because
            // IoT box can't find a printer.
            if (!printResult || printResult.result === false) {
                this.receiptQueue.length = 0;
                return this.getResultsError(printResult);
            }
        }
        return { successful: true };
    },
});