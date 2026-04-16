/** @odoo-module */

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(PaymentScreen.prototype, {
   shouldDownloadInvoice() {
        if (this.pos?.config?.disable_auto_invoice_download){
            debugger;
            return false;
        }
        return super.shouldDownloadInvoice();
    },
});
