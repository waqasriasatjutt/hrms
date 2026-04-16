/** @odoo-module */
import {PaymentInterface} from "@point_of_sale/app/payment/payment_interface";
import {AlertDialog} from "@web/core/confirmation_dialog/confirmation_dialog";
import {_t} from "@web/core/l10n/translation";

export class PaymentCompago extends PaymentInterface {
    setup() {
        super.setup(...arguments);
        this.payment_intent = {};
    }

    async send_payment_request(cid) {
        await super.send_payment_request(...arguments);
        return this._create_payment_intent(cid);
    }

    async send_payment_cancel(order, cid) {
        await super.send_payment_cancel(...arguments);
        return this._cancel_payment_intent();
    }

    async _create_payment_intent(cid) {
        const order = this.pos.get_order();
        const line = order.get_selected_paymentline();

        try {
            line.set_payment_status("waitingCapture");

            const payment_intent = await this.env.services.orm.silent.call(
                "pos.payment.method",
                "compago_create_payment_intent",
                [
                    [line.payment_method_id.id],
                    {
                        amount: line.amount,
                        currency: this.pos.currency.name,
                        reference: `${this.pos.config.current_session_id.id}_${line.payment_method_id.id}_${order.uuid}_${Math.random().toString(36).slice(2, 10)}`
                    }
                ]
            );

            if (!("id" in payment_intent)) {
                this._show_error(payment_intent.errorMessage);
                return false;
            }

            this.payment_intent = payment_intent;
            line.set_payment_status("waitingCard");

            return await this._wait_for_payment_intent_status(payment_intent.id);
        } catch (error) {
            this._show_error(error.message);
            return false;
        }
    }

    async _cancel_payment_intent() {
        clearTimeout(this.pollingTimeout);

        const line = this.pos.get_order().get_selected_paymentline();

        try {
            if ("id" in this.payment_intent) {
                await this.env.services.orm.silent.call(
                    "pos.payment.method",
                    "compago_cancel_payment_intent",
                    [[line.payment_method_id.id], this.payment_intent.id]
                );
            }
        } catch (error) {
            this._show_error(error.message);
        }

        return true;
    }

    _open_payment_intent(payment_intent_id) {
        setTimeout(() => {
            const url = `compago-pos-app:///charge/payment-intent/${payment_intent_id}`;

            const iframe = document.createElement('iframe');
            iframe.style.display = 'none';
            iframe.src = url;

            document.body.appendChild(iframe);

            // Remove the iframe after 1 second so it doesn't stay in the DOM
            setTimeout(() => document.body.removeChild(iframe), 1000);
        });
    }

    async _wait_for_payment_intent_status(payment_intent_id) {
        const request_interval = 3000;

        if (this.payment_method_id.compago_should_deep_link_to_app) {
            this._open_payment_intent(payment_intent_id);
        }

        const fetch_status = async (resolve, reject) => {
            clearTimeout(this.pollingTimeout);

            // If the user navigates to another screen, stop the polling
            if (this.pos.mainScreen.component.name !== "PaymentScreen") {
                return;
            }

            const order = this.pos.get_order();
            const line = order.get_selected_paymentline();

            const payment_intent = await this.env.services.orm.silent.call(
                "pos.payment.method",
                "compago_get_payment_intent_status",
                [[line.payment_method_id.id], payment_intent_id]
            );

            if ("paymentSummary" in payment_intent && payment_intent.paymentSummary?.status === "SUCCESS") {
                line.set_payment_status("done");
                resolve(true);
            } else if (payment_intent.expired || payment_intent.status === 'CANCELLED') {
                line.set_payment_status("retry");
                resolve(false);
            } else {
                this.pollingTimeout = setTimeout(() => fetch_status(resolve, reject), request_interval);
            }
        }

        return new Promise(fetch_status);
    }

    _show_error(error_msg, title) {
        this.env.services.dialog.add(AlertDialog, {
            title: title || _t("Compago Error"),
            body: error_msg,
        });
    }
}
