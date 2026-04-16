/**@odoo-module **/
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { _t } from "@web/core/l10n/translation";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { patch } from "@web/core/utils/patch";
patch(ControlButtons.prototype, {
    async onClickReturnReason() {
        const reasons = await this.get_return_reasons();
        const reasonslist = this.getReasonsList(reasons);
        const payload = await makeAwaitable(this.dialog, SelectionPopup, {
            title: _t("Select the product return reason"),
            list: reasonslist,
        });

        if (payload) {
            this.selectReason(payload);
        }
    },

    async get_return_reasons() {
        const reasons = await this.pos.data.searchRead(
            "pos.return.reason",
            [],
            ['id', 'name'],
            {}
        );
        return reasons;
    },

    /**
     * @returns {Array}
     */
    getReasonsList(reasons) {
        const selectionList = reasons.map((reason) => ({
            id: reason.id,
            label: reason.name,
            isSelected:
                this.currentOrder.return_reason_id &&
                reason.id === this.currentOrder.return_reason_id.id,
            item: reason,
        }));
        return selectionList;
    },
    async selectReason(reason) {
        await this.pos.get_order().setReturnReason(reason);
    }
});

