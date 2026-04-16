/** @odoo-module */

/*
 * Copyright (C) 2025 Axcelere.
 * Licensed under the GPL-3.0 License or later.
 */

import { _t } from "@web/core/l10n/translation";
import { PaymentInterface } from "@point_of_sale/app/payment/payment_interface";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

export class PaymentMpqr extends PaymentInterface {
    setup() {
        super.setup(...arguments);
    }

    get fast_payments() {
        return false;  // This enables manual "Send" button
    }
    async _mpqrFetchPaymentIntent (payment_method, pos_session, order, amount) {
        try {
            if (!order._isRefundOrder()){
                // Obtener las líneas de la orden con product_id y qty (solo datos primitivos)
                const order_lines = order.get_orderlines().map(line => {
                    const product_id = line.product_id.id;
                    const qty = line.quantity || line.qty || 1;
                    const price_unit = line.price_subtotal_incl || line.price_unit || 0;
                    
                    return {
                        product_id: Number(product_id),
                        qty: Number(qty), 
                        price_unit: Number(price_unit)
                    };
                });
                
                let data = await this.pos.data.silentCall(
                    "pos.payment.method",
                    "mpqr_make_payment",
                    [[payment_method], pos_session, amount, order.uuid, order_lines],
                );
                return data
            }else{
                const get_orderlines = order.get_orderlines()

                let original_pos_order_id = null;
                let toRefundLines_ids = []

                for (let line of get_orderlines){
                    toRefundLines_ids.push(line.id);
                    if (line.refunded_orderline_id && line.refunded_orderline_id.order_id) {
                        original_pos_order_id = line.refunded_orderline_id.order_id.id;
                    }
                }


                let data = await this.pos.data.silentCall(
                    "pos.order",
                    "mpqr_make_refunds",
                    [[], {
                        'pos_session_id': pos_session,
                        'amount_total': amount,
                        'payment_method_id': payment_method,
                        'original_pos_order_id': original_pos_order_id
                    }],
                );
                return data
            }
        } catch (error) {
            let message;
            if (error.code === 200) {
                message = error.data.message;
            } else {
                message = error.message;
            }
            this._showError(message);
            return false;
        };
    }
    async _mpqrMakePayment () {
        let _order = this.pos?.get_order()
        let line = _order.get_selected_paymentline();
        let payment_intent = await this._mpqrFetchPaymentIntent(
            line.payment_method_id.id,
            odoo.pos_session_id,
            _order,
            line.amount,
        );
        if (!payment_intent) {
            line.set_payment_status("retry");
            return false;
        }
        if (payment_intent['state'] === "Unauthorized" || payment_intent['state'] === "PAYMENT_FAILED") {
            console.log('Error no autorizado')
            line.set_payment_status("retry");
            this._showError(payment_intent['error']);
            return false;
        }
        _order.access_token_payment = payment_intent['transaction_id']
        line.transaction_id = payment_intent['transaction_id']
        line.set_payment_status("done");
        return true;
    }

    /**
     * @Override
     * @param { string } uuid
     * @returns Promise
     */
    async send_payment_request (cid) {
        super.send_payment_request(...arguments);
        const line = this.pos?.get_order().get_selected_paymentline();
        if (line.payment_method_id.use_payment_terminal === "mpqr"){
            line.set_payment_status("waiting");
            try {
                await this._mpqrMakePayment();
                return await new Promise((resolve) => {
                    this.webhook_resolver = resolve;
                });
            } catch (error) {
                this._showError(error);
                return false;
            }
        }
    }

    send_payment_cancel (order, cid) {
        super.send_payment_cancel(...arguments);
        return true;
    }

    _showError(error_msg, title) {
        this.env.services.dialog.add(AlertDialog, {
            title: title || _t("MP QR Error"),
            body: error_msg,
        });
    }
}
