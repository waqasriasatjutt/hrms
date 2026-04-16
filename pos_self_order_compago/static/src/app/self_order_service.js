import { patch } from "@web/core/utils/patch";
import { SelfOrder } from "@pos_self_order/app/self_order_service";
import { Compago, CompagoError } from "@pos_self_order_compago/app/compago";

patch(SelfOrder.prototype, {
    async setup() {
        await super.setup(...arguments);

        const paymentMethod = this.models["pos.payment.method"].find(
            (p) => p.use_payment_terminal === "compago"
        );

        if (paymentMethod) {
            this.compago = new Compago(
                this.env,
                paymentMethod,
                this.access_token,
                this.config,
                this.handleCompagoError.bind(this)
            );
        }
    },

    filterPaymentMethods(pms) {
        const paymentMethods = super.filterPaymentMethods(...arguments);
        const compagoPaymentMethods = pms.filter((rec) => rec.use_payment_terminal === "compago");

        return [...new Set([...paymentMethods, ...compagoPaymentMethods])];
    },

    handleCompagoError(error, type) {
        this.paymentError = true;
        this.handleErrorNotification(error, type);
    },

    handleErrorNotification(error, type = "danger") {
        if (error instanceof CompagoError) {
            this.notification.add(`Compago POS: ${error.message}`, { type: type, });
        } else {
            super.handleErrorNotification(...arguments);
        }
    },
});
