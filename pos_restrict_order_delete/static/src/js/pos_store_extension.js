/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";

patch(PosStore.prototype, {
    /**
     * Override closeSession to check for unpaid orders.
     */
    async closeSession() {
        const openOrders = this.get_open_orders();
        // Filter orders that are NOT paid and have a total > 0
        // We ensure they are effectively "active" orders on the floor/screen
        const unpaidOrders = openOrders.filter(order => {
            const isPaid = order.is_paid ? order.is_paid() : false;
            const total = typeof order.get_total_with_tax === 'function' ? order.get_total_with_tax() : (order.get_total_with_tax ? order.get_total_with_tax() : 0);
            return !isPaid && total > 0 && !order.finalized;
        });

        if (unpaidOrders.length > 0) {
            this.dialog.add(AlertDialog, {
                title: _t("Cannot Close Session"),
                body: _t(`There are ${unpaidOrders.length} unpaid active orders. Please pay or delete them before closing the session.`),
            });
            return;
        }

        return super.closeSession(...arguments);
    }
});
