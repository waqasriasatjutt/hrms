/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";

patch(PaymentScreen.prototype, {
    async addNewPaymentLine(paymentMethod) {
        const due = this.currentOrder.get_due();
        if (this.pos.config.guard_duplicate_zero_payment_line) {
            if (due <= 0) return false;
            const existingZeroLine = (this.paymentLines || []).find(
                (line) =>
                    line.payment_method_id?.id === paymentMethod.id &&
                    !line.paid &&
                    line.amount === 0
            );

            if (existingZeroLine) {
                return false;
            }
        }

        return await super.addNewPaymentLine(...arguments);
    },
});
