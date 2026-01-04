import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
const { DateTime } = luxon;

patch(PosStore.prototype, {

    async onDeleteOrder(order) {
    	if(this.get_cashier()._is_restrict_cancel_order){
    		this.dialog.add(AlertDialog, {
                title: _t("Access Error"),
                body: _t("You don't have access to cancel or delate the order. Please contact your manager."),
            });
    		return;
    	}
    	return super.onDeleteOrder(...arguments);
    },

    getPrintingChanges(order, diningModeUpdate) {
        const time = DateTime.now().toFormat("HH:mm");
        return {
            table_name: order.table_id ? order.table_id.table_number : "",
            config_name: order.config.name,
            time: time,
            tracking_number: order.tracking_number,
            // takeaway: order.config.takeaway && order.takeaway,
            takeaway: order.takeaway,
            employee_name: order.employee_id?.name || order.user_id?.name,
            custom_note: order.custom_note,
            order_note: order.general_note,
            diningModeUpdate: diningModeUpdate,
        };
    }

});