import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(PosOrder.prototype, {
	set_prescription(prescription_id) {
        debugger
		if (prescription_id) {
            this.update({ prescription_id: prescription_id });
        } else {
            this.update({ prescription_id: false });
        }
    },
});