import { _t } from "@web/core/l10n/translation";
import { NumberPopup } from "@point_of_sale/app/utils/input_popups/number_popup";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { patch } from "@web/core/utils/patch";

patch(ControlButtons.prototype, {
	async clickSetSubTotal() {
		this.dialog.add(NumberPopup, {
			title: _t('Amount to add'),
			startingValue: 0,
			getPayload: (num) => {
				this.apply_subtotal(num);
			},
		});
	},
	// Need to Improve
	async apply_subtotal(pc) {
        const order = this.pos.get_order();
        const selectedLine = order ? order.get_selected_orderline() : null;
        console.log(selectedLine);
        if (selectedLine.product_id.is_subtotal_to_qty_pp){
            const qty = pc / selectedLine.get_lst_price();
            selectedLine.set_quantity(qty);
            return true;
        }else{
            this.dialog.add(AlertDialog, {
				title: _t('Product Allow Permission'),
				body: _t(
					'The product is not allow to convert from subtotal to qty'
				),
			});
            return;
        }
			
	},
});
