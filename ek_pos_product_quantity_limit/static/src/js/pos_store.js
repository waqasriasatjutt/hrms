/** @odoo-module **/
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import RestrictQuantityPopup from "@ek_pos_product_quantity_limit/js/RestrictQuantityPopup";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

patch(ProductScreen.prototype, {
    async addProductToOrder(product) {
        const currentOrder = this.pos.get_order(); // Get the current order
        const maxLines =  this.pos.config.pos_bill_quantity_limit; // Assuming this is your limit
        // const currentLineCount = currentOrder.orderlines.length; // Count current lines
        const currentLineCount = currentOrder.lines.length;

        //  Check if adding another product exceeds the limit
        if (maxLines && currentLineCount >= maxLines) {
            
            this.dialog.add(AlertDialog, {
                title: _t("Limit of product Exceeded"),
                body: _t('Can not add more than '+ maxLines +' Products',),
            });
            return; // Exit if limit is exceeded
        } else {
            
            await super.addProductToOrder(product)

        }
        
        await super.addProductToOrder(product)
    },
});

