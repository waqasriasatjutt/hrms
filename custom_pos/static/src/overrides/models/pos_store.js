import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";


patch(PosStore.prototype, {
    async setDiscountpriceFromUI(line, val){
        line.set_discount_price(val);
    },
    getReceiptHeaderData(order) {
        // ✅ correct way inside patch
        // const result = this._super(order);
        const result = super.getReceiptHeaderData(order);
        // ✅ NEVER use selectedOrder (reprint-safe)
        result.partner = order?.get_partner?.() || null;

        // ✅ cashier must survive reprint
        result.cashier = _t(
            "Served by %s",
            order?.getCashierName?.()
            || this.get_cashier?.()?.name
            || this.config.name
        );

        return result;
    },
    // async pay() {
    //     const currentOrderPOS = this.get_order();
    //     if (!currentOrderPOS.get_partner()) {
    //         this.dialog.add(AlertDialog, {
    //             title: _t("Customer is Required"),
    //             body: _t("Customer is required to proceed with the order!"),
    //         });
    //         return;
    //     }
    //     await super.pay(...arguments);
    // },
})