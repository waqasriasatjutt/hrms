/** @odoo-module **/

import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";
import { roundPrecision } from "@web/core/utils/numbers";

patch(PosOrder.prototype, {
get_total_discount() {
    const ignored_product_ids = this._get_ignored_product_ids_total_discount();
    const discountProductId = this.config.discount_product_id?.id;

    return roundPrecision(
        this.lines.reduce((sum, orderLine) => {
            const productId = orderLine.product_id.id;

            if (ignored_product_ids.includes(productId)) {
                return sum;
            }

            const prices = orderLine.get_all_prices();

            // 1️⃣ Standard discounts (existing logic)
            sum += prices.priceWithTaxBeforeDiscount - prices.priceWithTax;

            if (
                orderLine.display_discount_policy() === "without_discount" &&
                orderLine.price_type !== "manual" &&
                orderLine.discount === 0
            ) {
                sum +=
                    (orderLine.get_taxed_lst_unit_price() -
                        orderLine.getUnitDisplayPriceBeforeDiscount()) *
                    orderLine.get_quantity();
            }

            // 2️⃣ YOUR CUSTOM DISCOUNT AMOUNT (negative manual line)
            if (
                discountProductId &&
                productId === discountProductId &&
                prices.priceWithTax < 0
            ) {
                sum += Math.abs(prices.priceWithTax);
            }

            return sum;
        }, 0),
        this.currency.rounding
    );
},


});
