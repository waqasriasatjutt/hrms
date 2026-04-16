/** @odoo-module **/

import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { formatCurrency } from "@point_of_sale/app/models/utils/currency";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";

patch(PosOrderline.prototype, {

    set_unit_price(price) {
        console.log(`Setting unit price to ${price}`);
        const result = super.set_unit_price(...arguments);
        this._checkPriceBelowCost(false);
        return result;
    },

    setUnitPrice(price) {
        console.log(`Setting unit price to ${price}`);
        const result = super.setUnitPrice(...arguments);
        this._checkPriceBelowCost();
        return result;
    },

    set_discount(discount) {
        console.log(`Setting discount to ${discount}%`);
        const result = super.set_discount(...arguments);
        this._checkPriceBelowCost(false);
        return result;
    },

    setDiscount(discount) {
        console.log(`Setting discount to ${discount}%`);
        const result = super.setDiscount(...arguments);
        this._checkPriceBelowCost();
        return result;
    },
    
    set_quantity(quantity, keep_price) {
        console.log(`Setting quantity to ${quantity}`);
        const result = super.set_quantity(...arguments);
        this._checkPriceBelowCost(false);
        return result;
    },

    setQuantity(quantity, keep_price) {
        console.log(`Setting quantity to ${quantity}`);
        const result = super.setQuantity(...arguments);
        this._checkPriceBelowCost();
        return result;
    },

    _checkPriceBelowCost(saas=true) {
        const product = saas ? this.getProduct(): this.get_product();
        if (!product) {
            console.log("No product found in orderline");
            return;
        }
        
        // Get cost and effective price after discount
        const cost = product.standard_price || 0;
        const effectivePrice = saas ? this.getUnitPrice() * (1 - (this.getDiscount() / 100)): this.get_unit_price() * (1 - (this.get_discount() / 100));
        
        console.log(`Checking price for ${product.display_name}: Price=${saas ? this.getUnitPrice():this.get_unit_price()}, Discount=${saas?this.getDiscount():this.get_discount()}%, Effective=${effectivePrice}, Cost=${cost}`);
        
        // If price is below cost and not zero (zero could be a gift or special case)
        if (effectivePrice < cost && effectivePrice > 0) {
            console.warn(`PRICE BELOW COST DETECTED: ${effectivePrice} < ${cost}`);

            alert(
                _t("Price Below Cost") + "\n\n" +
                _t("You cannot sell this product below its cost price.") +
                "\n" + _t("Cost Price: ") + formatCurrency(cost, this.currency)
            );

            
            // Reset the price to cost price
            saas ? super.setUnitPrice(cost): super.set_unit_price(cost);
            
            // Remove any discount
            if (saas && this.getDiscount() > 0 || !saas && this.get_discount() > 0) {
                saas?super.setDiscount(0):super.set_discount(0);
            }
            
            console.log("Price corrected to match cost price");
        }
    },
});

patch(PaymentScreen.prototype, {
    async validateOrder(isForceValidate) {
        // Get current order
        const order = this.currentOrder;
        if (!order) return super.validateOrder(...arguments);
        
        // Flag to track if we found any issues
        let hasIssues = false;
        const invalidLines = [];
        // Check each line
        const orderlines = order.getOrderlines?order.getOrderlines():order.get_orderlines();
        for (const line of orderlines) {
            const product = order.getOrderlines ? line.getProduct(): line.get_product();
            if (!product) continue;
            
            const cost = product.standard_price || 0;
            const effectivePrice = order.getOrderlines ? line.getUnitPrice() * (1 - (line.getDiscount() / 100)):line.get_unit_price() * (1 - (line.get_discount() / 100));
            
            // If price is below cost and not zero
            if (effectivePrice < cost && effectivePrice > 0) {
                invalidLines.push({
                    product: product,
                    line: line,
                    cost: cost,
                    price: effectivePrice
                });
                hasIssues = true;
            }
        }
        
        // If any issues found, show error and fix prices
        if (hasIssues) {
            let message = _t("The following products are priced below cost:") + "\n\n";
            
            for (const item of invalidLines) {
                message += `- ${item.product.display_name}: ${formatCurrency(item.price, false)} < ${formatCurrency(item.cost, false)}\n`;
                
                // Auto-fix the price
                order.getOrderlines?item.line.setUnitPrice(item.cost):item.line.set_unit_price(item.cost);
                if (order.getOrderlines && item.line.getDiscount() > 0 || order.get_orderlines && item.line.get_discount() > 0) {
                    order.getOrderlines?item.line.setDiscount(0):item.line.set_discount(0);
                }
            }
            
            message += "\n" + _t("Prices have been adjusted to match cost prices.");
            
            await this.dialog.add(AlertDialog, {
                title: _t("Cannot Proceed to Payment"),
                body: message
            });
            
            return false;
        }
        
        // If all checks pass, proceed with original validation
        return super.validateOrder(...arguments);
    }
});
