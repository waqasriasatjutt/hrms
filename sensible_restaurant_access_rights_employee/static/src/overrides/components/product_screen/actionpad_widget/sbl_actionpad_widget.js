/** @odoo-module */
import { ActionpadWidget } from "@point_of_sale/app/screens/product_screen/action_pad/action_pad";
import { patch } from "@web/core/utils/patch";

patch(ActionpadWidget.prototype, {
    get sblHidePayment() {
        const employee = this.pos.get_cashier();
        return employee?.sbl_hide_pos_payment || false;
    },
    get sblHideOrderButton() {
        const employee = this.pos.get_cashier();
        return employee?.sbl_hide_restaurant_order_button || false;
    },
    get sblShowOriginalPayButton() {
        // Original pay button should show when:
        // 1. Not in swap mode (swapButton is false)
        // 2. Employee is allowed to see payment
        return !this.swapButton && !this.sblHidePayment;
    },
    get sblShowRestaurantPayButton() {
        // Restaurant pay button should show when:
        // 1. Order is not empty
        // 2. Employee is allowed to see payment
        return this.currentOrder && !this.currentOrder.is_empty() && !this.sblHidePayment;
    },
});
