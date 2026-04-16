/** @odoo-module **/
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { useState, useRef } from "@odoo/owl";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { _t } from "@web/core/l10n/translation";


patch(PaymentScreen.prototype, {
    setup() {
        super.setup();

        this.state = useState({
            enabled: this.pos.config.enable_multicurrency,
            showOptions: false,
            currencies: this.pos.currency.currency_params || [],
            selectedCurrencyId: null,
            currentCurrency: null,
            inputAmount: "",
            remainingForeign: 0,
            changeForeign: 0,
        });
        this.multiCurrencyInputRef = useRef("multiCurrencyInput");
    },

    /* ---------------------------
       UI Actions
    ----------------------------*/

    toggleOptions() {
        this.state.showOptions = !this.state.showOptions;
    },

    onCurrencyChange(ev) {
        const currencyId = parseInt(ev.target.value);
        this.state.selectedCurrencyId = currencyId;

        this.state.currentCurrency = this.state.currencies.find(
            c => c.id === currencyId
        ) || null;

        this.state.remainingForeign = 0;
        this.state.changeForeign = 0;
    },

    _hasMultiCurrencyPaymentLine() {
        return this.currentOrder.paymentlines.some(
            line => line.converted_currency
        );
    },

    async addMultiCurrencyPayment() {
        // Prevent multiple multi-currency payments
        if (this._hasMultiCurrencyPaymentLine()) {
            this.popup.add(ErrorPopup, {
                title: _t('Payment Error'),
                body: _t("Only one multi-currency payment allowed per order."),
            });
            return;
        }

        if (!this.state.currentCurrency) return;

        const inputEl = this.multiCurrencyInputRef.el;
        if (!inputEl) return;

        const amountForeign = parseFloat(inputEl.value);
        if (!amountForeign || amountForeign <= 0) return;

        const order = this.currentOrder;
        const baseAmount = amountForeign / this.state.currentCurrency.rate;

        // Add payment line safely
        this.addNewPaymentLine(this.payment_methods_from_config[0]);
        await this.selectedPaymentLine.set_amount(baseAmount);

        this.selectedPaymentLine.converted_currency = {
            name: this.state.currentCurrency.display_name,
            symbol: this.state.currentCurrency.symbol,
            amount: amountForeign,
        };

        const totalBase = order.get_total_with_tax();
        const paidBase = order.get_total_paid();

        this.state.remainingForeign = Math.max(0, totalBase - paidBase) * this.state.currentCurrency.rate;
        this.state.changeForeign = Math.max(0, paidBase - totalBase) * this.state.currentCurrency.rate;

        inputEl.value = "";
    },




    deletePaymentLine() {
        super.deletePaymentLine(...arguments);
        this.state.remainingForeign = 0;
        this.state.changeForeign = 0;
    },

    /* ---------------------------
       Getters (computed values)
    ----------------------------*/

    get convertedTotal() {
        if (!this.state.currentCurrency) return 0;
        return this.currentOrder.get_total_with_tax() * this.state.currentCurrency.rate;
    },

    get currencySymbol() {
        return this.state.currentCurrency?.symbol || "";
    },

    /* ---------------------------
       Export / Validation
    ----------------------------*/

    async _finalizeValidation() {
        const order = this.currentOrder;

        order.paymentlines.forEach(line => {
            if (line.converted_currency) {
                line.payment_currency = line.converted_currency.name;
                line.currency_amount = line.converted_currency.amount;
                line.currency_symbol = line.converted_currency.symbol;
            }
        });

        if (this.state.currentCurrency) {
            order.converted_currency_total =
                order.get_total_with_tax() * this.state.currentCurrency.rate;
            order.converted_currency_change =
                order.get_change() * this.state.currentCurrency.rate;
            order.converted_currency_symbol =
                this.state.currentCurrency.symbol;
        }

        await super._finalizeValidation();
    },
});
