/** @odoo-module */
import { _t } from "@web/core/l10n/translation";
import { PaymentInterface } from "@point_of_sale/app/payment/payment_interface";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

export class PaymentUnicobros extends PaymentInterface {
    async create_payment_intent() {
        const order = this.pos.get_order();
        const line = order.get_selected_paymentline();
        // Build informations for creating a payment intend on Unicobros.
        // Data in "reference" are send back with the webhook notification
        const baseUrl = window.location.origin;
        const infos = {
            total: line.amount,
            currency: "ARS",
            description: "Test",
            reference: `${this.pos.config.current_session_id.id}_${line.payment_method_id.id}_${order.uuid}`,
            test: false,
            webhook: `${baseUrl}/unicobros/notification`,
        };

        // uni_payment_intent_create will call the Unicobros api
        return await this.env.services.orm.silent.call(
            "pos.payment.method",
            "uni_payment_intent_create",
            [[line.payment_method_id.id], infos]
        );
    }

    async cancel_payment_intent() {
        const line = this.pos.get_order().get_selected_paymentline();
        // uni_payment_intent_cancel will call the Unicobros api
        return await this.env.services.orm.silent.call(
            "pos.payment.method",
            "uni_payment_intent_cancel",
            [[line.payment_method_id.id]]
        );
    }

    setup() {
        super.setup(...arguments);
        this.webhook_resolver = null;
        this.payment_intent = {};
    }

    async send_payment_request(cid) {
        await super.send_payment_request(...arguments);
        const line = this.pos.get_order().get_selected_paymentline();
        try {
            // During payment creation, user can't cancel the payment intent
            line.set_payment_status("waitingCapture");
            // Call Unicobros to create a payment intent
            const payment_intent = await this.create_payment_intent();
            if ("error" in payment_intent) {
                this._showMsg(payment_intent.error, "error");
                return false;
            }
            // Payment intent creation successfull, save it
            this.payment_intent = payment_intent;
            // After payment creation, make the payment intent canceling possible
            line.set_payment_status("waitingCard");
            // Wait for payment intent status change and return status result
            return await new Promise((resolve) => {
                this.webhook_resolver = resolve;
            });
        } catch (error) {
            this._showMsg(error, "System error");
            return false;
        }
    }

    async send_payment_cancel(order, cid) {
        await super.send_payment_cancel(order, cid);
        
        // If there is no payment intent id, nothing to cancel on Unicobros
        const uid = this.payment_intent?.data?.uid;
        if (!uid) {
            return true;
        }
        const canceling_status = await this.cancel_payment_intent();
        
        if ("error" in canceling_status) {
            const message =
                canceling_status.status === 409
                    ? _t("Payment has to be canceled on terminal")
                    : _t("Payment not found (canceled/finished on terminal)");
            this._showMsg(message, "info");
            return canceling_status.status !== 409;
        }
        return true;
    }

    async handleUnicobrosWebhook(info) {
        const line = this.pos.get_order().get_selected_paymentline();
        
        const showMessageAndResolve = (messageKey, status, resolverValue) => {
            if (!resolverValue) {
                this._showMsg(messageKey, status);
            }
            line.set_payment_status("done");
            this.webhook_resolver?.(resolverValue);
            return resolverValue;
        };
        if (info.card_brand_unicobros) {
            line.payment_method_payment_mode = info.payment_mode_unicobros;
            line.cardholder_name = info.cardholder_name_unicobros;
            line.card_no = info.card_no_unicobros;
            line.card_brand = info.card_brand_unicobros;
        }

        if (info.status_payment_unicobros === "200") {
            return showMessageAndResolve(_t("Payment has been processed"), "info", true);
        }
        return showMessageAndResolve(_t("El pago fue rechazado: " + info.status_description_unicobros), "info", false);

    }

    // private methods
    _showMsg(msg, title) {
        this.env.services.dialog.add(AlertDialog, {
            title: "Unicobros " + title,
            body: msg,
        });
    }
}
