/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { useState, onWillStart } from "@odoo/owl";

patch(OrderReceipt.prototype, {

    setup() {
        super.setup();

        this.state = useState({
            invoiceNumber: "N/A",
        });

        onWillStart(async () => {

            try {

                const orderName = this.props.data.name;

                // Generate barcode
                this.props.data.pos_barcode =
                    `${window.location.origin}/report/barcode/?barcode_type=Code128&value=${encodeURIComponent(orderName)}`;

                // Get invoice number from backend
                const invoice = await this.env.services.orm.call(
                    "pos.order",
                    "get_invoice_number",
                    [orderName]
                );

                if (invoice) {
                    this.state.invoiceNumber = invoice;
                }

            } catch (error) {
                console.error("POS Receipt Error:", error);
            }

        });

    },

});


//patch(Order.prototype, {
//    export_for_printing() {
//        const data = super.export_for_printing(...arguments);
//
//        const barcodeValue = this.name;
//
//        // Simply set the barcode URL (no async fetch)
//        data.pos_barcode = `${window.location.origin}/report/barcode/?barcode_type=Code128&value=${encodeURIComponent(barcodeValue)}`;
//
//        return data;
//    },
//});