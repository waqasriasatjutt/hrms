/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { CashMovePopup } from "@point_of_sale/app/navbar/cash_move_popup/cash_move_popup";
import { onWillStart, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { sprintf } from "@web/core/utils/strings";

patch(CashMovePopup.prototype, {
    setup() {
        super.setup();
        this.state = useState({
            ...this.state,
            errorMessage: "",
            cashSummary: { amount: 0 },
        });

        onWillStart(async () => {
            try {
                const result = await this.pos.getClosePosInfo();
                this.state.cashSummary = result?.default_cash_details ?? { amount: 0 };
            } catch (e) {
                console.error("Failed to fetch cash summary:", e);
            }
        });
    },

    async confirm() {
        const output_amount = parseFloat(this.state.amount || 0);
        const cash_in_box = this.state.cashSummary?.amount ?? 0;

        if (
            this.pos.config.enable_cash_restriction &&
            this.state.type === 'out' &&
            (!Number.isFinite(output_amount) || output_amount > cash_in_box)
        ) {
            this.state.errorMessage = sprintf(
                _t("You are trying to withdraw %s but only %s is available. Please enter a lower amount."),
                this.env.utils.formatCurrency(output_amount),
                this.env.utils.formatCurrency(cash_in_box)
            );
            return false;
        }

        this.state.errorMessage = "";
        return super.confirm();
    }
});
