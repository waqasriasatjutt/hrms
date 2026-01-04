/** @odoo-module **/

import { PaymentScreenStatus } from "@point_of_sale/app/screens/payment_screen/payment_status/payment_status";
import { patch } from "@web/core/utils/patch";

patch(PaymentScreenStatus.prototype, {

    usd_rate: 1,
    lbp_rate: this.props?.order?.getLBPRate() || 89500
,    

    formatAmount(amount, rate) {
        const value = amount * rate;
        return this.env.utils.formatCurrency(value);
    },

    get remainingText() {
        const dueLbp = this.props.order.get_due() || 0;
        const remainingLbp = Math.max(dueLbp, 0);

        const isUsd = this.env.pos?.paymentScreen?.state?.isUsdPayment ?? false;
        if (isUsd) {
            const usd = remainingLbp / this.props.order.getLBPRate(); // convert LBP → USD
            return {
                usd: this.env.utils.formatCurrency(usd),
                lbp: this.env.utils.formatCurrency(remainingLbp),
            };
        } else {
            return {
                usd: this.env.utils.formatCurrency(remainingLbp / this.props.order.getLBPRate()),
                lbp: this.env.utils.formatCurrency(remainingLbp),
            };
        }
    },

    get changeText() {
        const dueLbp = this.props.order.get_due() || 0;
        const changeLbp = Math.max(-dueLbp, 0);

        const isUsd = this.env.pos?.paymentScreen?.state?.isUsdPayment ?? false;
        if (isUsd) {
const usd = changeLbp / this.props.order.getLBPRate();
return {
    usd: this.env.utils.formatCurrency(usd, { digits: [69, 2] }), // 2 decimal places
    lbp: this.env.utils.formatCurrency(changeLbp),
};
        } else {
            return {
                usd: this.env.utils.formatCurrency(changeLbp / this.props.order.getLBPRate()),
                lbp: this.env.utils.formatCurrency(changeLbp),
            };
        }
    },

    // ⚡ override addNewPayment
    addNewPayment(paymentMethod, amount) {
        const isUsd = this.env.pos?.paymentScreen?.state?.isUsdPayment ?? false;
        const convertedAmount = isUsd ? amount * this.props.order.getLBPRate() : amount;

        return super.addNewPayment(paymentMethod, convertedAmount);
    },
});
