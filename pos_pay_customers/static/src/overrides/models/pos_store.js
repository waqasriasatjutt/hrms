/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { _t } from "@web/core/l10n/translation";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { NumberPopup } from "@point_of_sale/app/utils/input_popups/number_popup";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

patch(PosStore.prototype, {
    async createCustomerPayment(partner) {
        const amount = await makeAwaitable(this.dialog, NumberPopup, {
            title: _t("Payout Amount"),
            startingValue: 0,
        });

        if (!amount || parseFloat(amount) <= 0) {
            return;
        }

        const payoutAmount = parseFloat(amount);

        const paymentMethods = this.config.payment_method_ids.filter(
            (method) => method.type != "pay_later"
        );
        const selectionList = paymentMethods.map((paymentMethod) => ({
            id: paymentMethod.id,
            label: paymentMethod.name,
            item: paymentMethod,
        }));

        const selectedPaymentMethod = await makeAwaitable(this.dialog, SelectionPopup, {
            title: _t("Select payment method for payout"),
            list: selectionList,
        });

        if (!selectedPaymentMethod) {
            return;
        }

        // Find customer account (pay_later) payment method
        const paylaterPaymentMethod = this.models["pos.payment.method"].find(
            (pm) => this.config.payment_method_ids.find(m => m.id === pm.id) && pm.type === "pay_later"
        );

        if (!paylaterPaymentMethod) {
            this.dialog.add(AlertDialog, {
                title: _t("Configuration Error"),
                body: _t("Customer Account (Pay Later) payment method must be configured in this Point of Sale to process payouts."),
            });
            return;
        }

        let newOrder;
        const emptyOrder = this.get_open_orders().find(
            (order) =>
                order.lines.length === 0 &&
                order.payment_ids.length === 0 &&
                (!order.partner || order.partner.id === partner.id)
        );
        if (emptyOrder) {
            newOrder = emptyOrder;
            this.set_order(newOrder);
        } else {
            newOrder = this.add_new_order();
        }

        newOrder.set_partner(partner);

        // 1. Add the actual payout line (e.g. Cash) - Negative
        const payoutPayment = newOrder.add_paymentline(selectedPaymentMethod);
        payoutPayment.set_amount(-Math.abs(payoutAmount));

        // 2. Add the balancing account line - Positive
        const balancingPayment = newOrder.add_paymentline(paylaterPaymentMethod);
        balancingPayment.set_amount(Math.abs(payoutAmount));

        newOrder.is_settling_account = true;

        this.showScreen("PaymentScreen", { orderUuid: this.selectedOrderUuid });
    },
});
