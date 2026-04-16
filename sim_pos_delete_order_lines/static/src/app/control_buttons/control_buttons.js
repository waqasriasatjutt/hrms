import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";


patch(ControlButtons.prototype, {

    async onClearLines() {
        var order = this.pos.get_order();
        var lines = order.get_orderlines();
        if (lines.length) {
            this.dialog.add(ConfirmationDialog, {
                title: _t("Clear Orders?"),
                body: _t("Are you sure you want to remove all items from your cart?"),
                confirm: () => {  lines.filter(line => line.get_product())
                .forEach(line => order.removeOrderline(line)); },
                confirmLabel: _t("Clear"),
                cancel: () => {},
                cancelLabel: _t("Cancel"),
            });
        }else{
            this.notification.add(_t("Your cart is already empty."), { type: "danger" });
        }
    }
})