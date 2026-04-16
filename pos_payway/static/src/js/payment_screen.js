/** @odoo-module */

/*
 * Copyright (C) 2025 Axcelere.
 * Licensed under the GPL-3.0 License or later.
 */


import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
import { onMounted } from "@odoo/owl";

patch(PaymentScreen.prototype, {

    setup() {
        super.setup(...arguments);
        onMounted(() => {
            const pendingPaymentLine = this.currentOrder.payment_ids.find(
                (paymentLine) =>
                    paymentLine.payment_method_id.use_payment_terminal === "payway" &&
                    !paymentLine.is_done() &&
                    paymentLine.get_payment_status() !== "pending"
            );
            if (pendingPaymentLine) {
                pendingPaymentLine.set_payment_status("force_done");
            }
        });
    },

    async validateOrder(isForceValidate) {
        console.log('ValidateOrder payway')
        let payment_type;
        const order = this.pos?.get_order();
        let line = order.get_selected_paymentline()

        if (line.payment_method_id && line.payment_method_id.use_payment_terminal === "payway"){
            if (line.amount > 0){
                payment_type = 'payments'
            }
            else{
                payment_type = 'reversals_refunds'
            }
            const result = await this.pos.data.silentCall("pos.order", "payway_payment_status", [1, {
                'amount_total': order.amount,
                'payment_method_id': line.payment_method_id.id,
                'pos_session_id': odoo.pos_session_id,
                'access_token_payment': order.access_token_payment,
                'payment_type_build': payment_type,
            }]);

            if ((result['payment_status'] === 'CONFIRMED' || result['payment_status'] === 'REVERSED') && result['status_code'] === 200){
                // Reset payment terminal state before validation
                this.pos.paymentTerminalInProgress = false;
                var result_new = await super.validateOrder(...arguments);
                return await this.pos.data.silentCall("pos.order", "payway_updating_order", [1, {
                    'access_token_payment': order.access_token_payment,
                    'access_token_order': order.access_token
                }]);
            }
            if ((result['payment_status'] !== 'CONFIRMED' || result['payment_status'] === 'REVERSAL_REQUEST') && result['status_code'] === 200){
                this.dialog.add(AlertDialog, {
                    title: ("Error"),
                    body:("Debe ser realizada la transacción antes de ser validada!"),
                });
                return false;
            }
            if (result['status_code'] !== 200){
                this.dialog.add(AlertDialog, {
                    title: ("Error"),
                    body:(result['error']),
                });
                return false;
            }
        }
        else{
            return super.validateOrder(...arguments);
        }
    },

    deletePaymentLine(uuid) {

        const order = this.pos?.get_order();
        if (!order) {
            console.error('❌ No order found');
            return false;
        }

        // Find the payment line by uuid
        const line = this.paymentLines.find((line) => line.uuid === uuid);

        if (line && line.payment_method_id.use_payment_terminal === "payway" && line.payment_status !== 'pending') {
            

            const payment_type = line.amount > 0 ? 'payments' : 'reversals_refunds';

            // Reset payment status before cancellation
            line.set_payment_status('');

            this.pos.data.silentCall("pos.order", "payway_make_cancel", [1, {
                'amount_total': line.amount,
                'payment_method_id': line.payment_method_id.id,
                'pos_session_id': odoo.pos_session_id,
                'access_token_payment': order.access_token_payment,
                'payment_type_build': payment_type,
            }]).then((result) => {
                console.log('✅ Payway cancellation request sent successfully:', result);
            }).catch((error) => {
                this.env.services.dialog.add(AlertDialog, {
                    title: "Error",
                    body: "Error trying to connect to terminal. Check your internet connection",
                });
            });

            // Always remove the payment line to clear the electronic payment state
            this.currentOrder.remove_paymentline(line);
            this.numberBuffer.reset();

            // Reset payment terminal state to allow new payments
            this.pos.paymentTerminalInProgress = false;

            // Force re-render to update UI
            this.render(true);
            return false;
        }
        return super.deletePaymentLine(uuid);
    },

    // deletePaymentLine(uuid) {
    //     console.log('deletePaymentLine payway')
    //     let payment_type;
    //     const line = this.paymentLines.find((line) => line.uuid === uuid);
    //     if (line.payment_method.use_payment_terminal === "payway" && line.payment_status !== 'pending') {
    //         if (line.amount > 0) {
    //             payment_type = 'payments'
    //         } else {
    //             payment_type = 'reversals_refunds'
    //         }
    //         try {
    //             this.orm.silent.call("pos.order", "payway_make_cancel", [1, {
    //                 'amount_total': line.amount,
    //                 'payment_method_id': line.payment_method.id,
    //                 'pos_session_id': line.order.pos_session_id,
    //                 'access_token_payment': line.order.access_token_payment,
    //                 'payment_type_build': payment_type,
    //             }]);
    //         } catch (_e) {
    //             this.popup.add(ErrorPopup, {
    //                 title: _t("Error"),
    //                 body: _t("Error trying to connect to terminal. Check your internet connection"),
    //             });
    //             return false;
    //         }
    //
    //         // If a paymentline with a payment terminal linked to
    //         // it is removed, the terminal should get a cancel
    //         // request.
    //         if (['waiting', 'waitingCard', 'timeout'].includes(line.get_payment_status())) {
    //             line.set_payment_status('waitingCancel');
    //             line.payment_method.payment_terminal.send_payment_cancel(this.currentOrder, cid).then(function () {
    //                 this.currentOrder.remove_paymentline(line);
    //                 this.numberBuffer.reset();
    //             })
    //         } else if (line.get_payment_status() !== 'waitingCancel') {
    //             this.currentOrder.remove_paymentline(line);
    //             this.numberBuffer.reset();
    //             this.render(true);
    //         }
    //     }
    //     return super.deletePaymentLine(uuid);
    // }
});
