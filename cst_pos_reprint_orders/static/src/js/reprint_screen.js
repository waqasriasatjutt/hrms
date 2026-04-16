/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { WarningDialog } from "@web/core/errors/error_dialogs";

patch(TicketScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this.dialog = useService("dialog");
    },

    /* Hide the Print icon On Ongoing state*/
    shouldShowPrintIcon(order){
       return this?._getScreenToStatusMap()[order?.get_screen_data().name] == 'ONGOING'
    },

    async onReprintOrder(order) {
        try {
            const hardwareProxy = this.pos?.hardwareProxy;

            if (hardwareProxy) {
                const connectionInfo = hardwareProxy.connectionInfo;

                if (connectionInfo?.status === "connected" && hardwareProxy.printer) {
                    await hardwareProxy.printer.printReceipt(order);
                } else {
                    await this.pos.printReceipt({ order });
                }
            } else {
                await this.pos.printReceipt({ order });
            }

        } catch (error) {

            this.dialog.add(WarningDialog, {
            title: _t("Printing Error"),
            message: _t(
                "Failed to print the receipt. Please check the printer connection."
            ),
        });

        }
    },
});
