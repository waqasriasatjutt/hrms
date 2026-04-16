/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { _t } from "@web/core/l10n/translation";

patch(ControlButtons.prototype, {
    removeAllLine() {
        var order = self.posmodel.get_order();
        var lines = self.posmodel.get_order().get_orderlines()
        var i = 0;
        while ( i < lines.length ) {
            order.removeOrderline (lines[i]);
        }
        self.posmodel.env.services.notification.add(_t("Your cart has been cleared!"), { type: "success" });
    }
});
