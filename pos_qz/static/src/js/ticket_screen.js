/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { _t } from "@web/core/l10n/translation";

patch(TicketScreen.prototype, {

    async doPrintSafe() {
        try {
            const order = this.getSelectedOrder();
            console.error("QZ Print 111:");

            if (!order) {
                return;
            console.error("QZ Print 111:ret");

            }
            console.error("QZ Print 111:reta");

            // if (!this.env.pos.printer) {
            //     await this.env.services.popup.add({
            //         title: _t("Printer Error"),
            //         body: _t("No printer is configured or connected."),
            //     });
            //     return;
            // }
            // this.print(order);
            // await this.doPrint.call(order);

        } catch (error) {
            console.error("QZ Print Error:", error);

            await this.env.services.popup.add({
                title: _t("Printing Failed"),
                body: _t("Failed in printing Detailed Receipt changes of the order"),
            });
        }
    },

});
