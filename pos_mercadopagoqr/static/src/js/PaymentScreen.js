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
                    paymentLine.payment_method_id.use_payment_terminal === "mpqr" &&
                    !paymentLine.is_done() &&
                    paymentLine.get_payment_status() !== "pending"
            );
            if (pendingPaymentLine) {
                pendingPaymentLine.set_payment_status("force_done");
            }
        });
    },

    async validateOrder(isForceValidate) {
        const order = this.pos?.get_order();
        const isRefundOrder = order._isRefundOrder()
        let line = order.get_selected_paymentline()
        if (line.payment_method_id && line.payment_method_id.use_payment_terminal === "mpqr"){
            const result = await this.pos.data.silentCall("pos.order", "mpqr_get_payment_status", [1, {
                'amount_total': order.amount,
                'payment_method_id': line.payment_method_id.id,
                'pos_session_id': odoo.pos_session_id,
                'access_token_payment': order.access_token_payment,
                'order_uid': order.uuid,
                'isRefundOrder': isRefundOrder,
            }]);
            if ((result['payment_status'] === 'paid' || result['payment_status'] === 'processed') && result['status_code'] === 200){
                order.mpqr_payment_id = result['payment_id'];
                // Reset payment terminal state before validation
                this.pos.paymentTerminalInProgress = false;
                var result_new = await super.validateOrder(...arguments);
                return await this.pos.data.silentCall("pos.order", "mpqr_updating_order", [1, {
                    'mpqr_payment_id': result['payment_id'],
                    'access_token_order': order.access_token,
                    'access_token_payment': order.access_token_payment,
                }]);
            }
            if ((result['payment_status'] !== 'paid' || result['payment_status'] !== 'processed') && result['status_code'] !== 200){
                this.dialog.add(AlertDialog, {
                    title: ("Error"),
                    body:result['error'],
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
            return false;
        }
        
        // Find the payment line by uuid
        const line = this.paymentLines.find((line) => line.uuid === uuid);
        
        if (line && line.payment_method_id.use_payment_terminal === "mpqr" && line.payment_status !== 'pending') {
            
            // const payment_type = line.amount > 0 ? 'payments' : 'reversals_refunds';
            
            // Reset payment status before cancellation
            line.set_payment_status('');
            
            this.pos.data.silentCall("pos.order", "mpqr_make_cancel", [1, {
                'amount_total': line.amount,
                'payment_method_id': line.payment_method_id.id,
                'pos_session_id': odoo.pos_session_id,
                'access_token_payment': order.access_token_payment,
            }]).then((result) => {
                if (result.success === false || result.status_code === 400) {
                    // Cancellation failed, show error and don't remove payment line
                    this.dialog.add(AlertDialog, {
                        title: "Error",
                        body: result.error || "No se puede cancelar este pago",
                    });
                    // Restore payment status
                    line.set_payment_status('done');
                } else {
                    // Cancellation successful, remove the payment line
                    this.currentOrder.remove_paymentline(line);
                    this.numberBuffer.reset();

                    // Reset payment terminal state to allow new payments
                    this.pos.paymentTerminalInProgress = false;
                }

                // Force re-render to update UI
                this.render(true);
            }).catch((error) => {
                this.env.services.dialog.add(AlertDialog, {
                    title: "Error",
                    body: "Error trying to connect to terminal. Check your internet connection",
                });
                // Restore payment status on error
                line.set_payment_status('done');
                this.render(true);
            });
            return false;
        }
        return super.deletePaymentLine(uuid);
    }
});
