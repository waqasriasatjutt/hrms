/** @odoo-module **/

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";

patch(ProductScreen.prototype, {
    setup() {
            super.setup();
            this.action = useService("action");
            this.orm = useService("orm");
    },

    // Raise the waring if product have no stock while click the product
    async addProductToOrder(product) {
        const stock_quant = await this.orm.call("product.product","action_get_warehouse_quant",[product.id,this.pos.config.id])
        if (stock_quant <= 0) {
            const message = `The selected product has no stock, so please update it and proceed with the order for - ${product.display_name}.`;
                this.dialog.add(AlertDialog, {
                        title: _t("Access Denied"),
                        body: _t(message),
                });
            return
        }
        super.addProductToOrder(product);

    }
     
})



