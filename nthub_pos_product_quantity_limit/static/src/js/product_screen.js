import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

patch(ProductScreen.prototype, {
    async onNumpadClick(buttonValue) {
        // Define currentInput outside the method to keep its state
        if (!this.currentInput) {
            this.currentInput = ""; // Initialize if not already set
        }

        if (["quantity", "discount", "price"].includes(buttonValue)) {
            this.numberBuffer.capture();
            this.numberBuffer.reset();
            this.pos.numpadMode = buttonValue;
            return;
        } else {
            const order_line = this.currentOrder.get_selected_orderline();
            const product_qty = order_line ? order_line.qty : 0; // Current quantity before changes
            const max_qty = order_line ? order_line.product_id.limit_quantity : 0;
            const check_limit = order_line ? order_line.product_id.is_product_quantity_limit : false;

            if (order_line) {
                // Concatenate button value to currentInput
                this.currentInput += buttonValue;
                const total = product_qty + buttonValue ;
                const totalQuantity = parseInt(this.currentInput, 10) || 0; // Convert concatenated string to integer
                const final_total = parseInt(total, 10) || 0; // Convert concatenated string to integer
                // Update the order line quantity
                order_line.set_quantity(final_total);

                // Validate against max quantity
                if (check_limit && max_qty > 0) {
                    

                    if (final_total > max_qty) {
                        

                        // Reset number buffer to prevent incorrect entry
                        this.numberBuffer.reset();
                        
                        // Show alert dialog for quantity limit exceeded
                        this.dialog.add(AlertDialog, {
                            title: _t("Quantity Limit Exceeded"),
                            // body: _t("The quantity you have entered exceeds the allowed limit. Please adjust the quantity."),
                            body: _t('Can not add more than '+ max_qty + ' piece for ' + order_line.product_id.display_name),
                        });
                        // Revert the quantity change
                        order_line.set_quantity(product_qty); // Reset to previous quantity
                        this.currentInput = ""; // Reset currentInput after reverting
                        return; // Stop further processing
                    }
                }

                // Call super function to ensure normal operation proceeds
                await super.onNumpadClick(buttonValue);
            } else {
                
            }
        }
    },
   
});

