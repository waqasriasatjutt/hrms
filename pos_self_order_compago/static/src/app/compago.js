import {_t} from "@web/core/l10n/translation";
import {rpc} from "@web/core/network/rpc";

export class CompagoError extends Error {
}

export class Compago {
    constructor(...args) {
        this.setup(...args);
    }

    setup(env, compago_payment_method, access_token, pos_config, error_callback) {
        this.env = env;
        this.accessToken = access_token;
        this.paymentMethod = compago_payment_method;
        this.posConfig = pos_config;
        this.errorCallback = error_callback;

        this.pollingTimeout = null;
        this.inactivityTimeout = null;
        this.paymentCancelled = false;
    }

    async startPayment(order) {
        const result = await this.processPayment(order);
        if (result) {
            await this.pollPaymentIntentStatus(result.orderAccessToken, result.paymentIntentId);
        }
    }

    async processPayment(order) {
        try {
            const response = await rpc(`/kiosk/payment/${this.posConfig.id}/kiosk`, {
                order: order.serialize({orm: true}),
                access_token: this.accessToken,
                payment_method_id: this.paymentMethod.id,
            });

            if (response) {
                const order = response.order[0];
                const paymentIntentResponse = response.payment_status;

                if ("id" in paymentIntentResponse) {
                    return {
                        orderAccessToken: order.access_token,
                        paymentIntentId: paymentIntentResponse.id
                    };
                } else {
                    this.errorCallback(new CompagoError(paymentIntentResponse.errorMessage || _t("Compago Error")))
                    return false;
                }
            }
        } catch (error) {
            this.errorCallback(error);
            return false;
        }
    }

    async pollPaymentIntentStatus(orderAccessToken, paymentIntentId) {
        this.inactivityTimeout = setTimeout(() => {
            this.paymentCancelled = true;
        }, 90000);

        const requestInterval = 3000;

        const fetchStatus = async (resolve, reject) => {
            clearTimeout(this.pollingTimeout);

            if (this.paymentCancelled) {
                await this.cancelPayment(orderAccessToken, paymentIntentId);
                resolve(false);
                return;
            }

            const paymentIntent = await rpc(
                "/pos-self-order/compago-payment-intent-status",
                {
                    access_token: this.accessToken,
                    order_access_token: orderAccessToken,
                    payment_intent_id: paymentIntentId,
                    payment_method_id: this.paymentMethod.id,
                }
            );

            const status = paymentIntent?.status;

            if (status === "CONFIRMED") {
                clearTimeout(this.inactivityTimeout);
                resolve(true);
            } else if (status === "PENDING") {
                this.pollingTimeout = setTimeout(() => fetchStatus(resolve, reject), requestInterval);
            } else {
                clearTimeout(this.inactivityTimeout);
                resolve(false);
            }
        }

        return new Promise(fetchStatus);
    }

    async cancelPayment(orderAccessToken, paymentIntentId) {
        try {
            await rpc("/pos-self-order/compago-cancel-payment-intent", {
                access_token: this.accessToken,
                order_access_token: orderAccessToken,
                payment_intent_id: paymentIntentId,
                payment_method_id: this.paymentMethod.id
            });
        } catch (error) {
            this.errorCallback(error, "warning");
        }

        this.disposePaymentIntent();
    }

    disposePaymentIntent() {
        this.paymentCancelled = false;
        clearTimeout(this.pollingTimeout);
        clearTimeout(this.inactivityTimeout);
    }
}
