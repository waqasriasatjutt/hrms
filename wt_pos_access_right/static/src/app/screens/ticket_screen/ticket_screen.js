import { _t } from "@web/core/l10n/translation";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { patch } from "@web/core/utils/patch";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

patch(TicketScreen.prototype, {
	async onDoRefund() {
        if (this.pos.get_cashier()._is_restrict_refund_order) {
            this.dialog.add(AlertDialog, {
                title: _t("Access Error"),
                body: _t("You don't have access to refund order. Please contect your manager."),
            });
    		return;
        }
        await super.onDoRefund(...arguments);
    },
});