/** @odoo-module **/

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { OrderTabs } from "@point_of_sale/app/components/order_tabs/order_tabs";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(PosStore.prototype, {
    canCreateNewOrder() {
        const config = this.config;

        if (!config.enable_order_limit) {
            return true;
        }

        const openOrders = this.get_open_orders();

        return openOrders.length < config.max_orders;
    },

    add_new_order() {
        if (!this.canCreateNewOrder()) {
            this.env.services.dialog.add(AlertDialog, {
                title: _t("Order Limit Exceeded"),
                body: _t(
                    "Order limit reached. Please complete or cancel existing orders."
                ),
            });
            return null;
        }

        return super.add_new_order(...arguments);
    },
});

patch(OrderTabs.prototype, {
    newFloatingOrder() {
        this.pos.selectedTable = null;
        const order = this.pos.add_new_order();

        // If add_new_order returned null due to our limit, stop here
        if (!order) {
            return;
        }

        this.pos.showScreen("ProductScreen");
        this.dialog.closeAll();
        return order;
    },
});
