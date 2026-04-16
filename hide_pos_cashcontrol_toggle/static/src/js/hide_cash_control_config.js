/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { OpeningControlPopup } from "@point_of_sale/app/store/opening_control_popup/opening_control_popup";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";

patch(PosStore.prototype, {
    openOpeningControl() {
        if (
            this.shouldShowOpeningControl() &&
            !this.config.hide_opening_cash_control
        ) {
            this.dialog.add(
                OpeningControlPopup,
                {},
                {
                    onClose: () => {
                        if (
                            this.session.state !== "opened" &&
                            this.mainScreen.component === ProductScreen
                        ) {
                            this.closePos();
                        }
                    },
                }
            );
        } else {
            console.log("Opening cash control popup skipped due to config.");
        }
    }
});
