/** @odoo-module **/

import { ComboConfiguratorPopup } from "@point_of_sale/app/store/combo_configurator_popup/combo_configurator_popup";
import { patch } from "@web/core/utils/patch";
import { onMounted } from "@odoo/owl";

patch(ComboConfiguratorPopup.prototype, {
    setup() {
        // Call the original setup
        super.setup();
        onMounted(() => {
            this.autoSelectSingleChoices();
            if (!this.hasMultipleChoices()) {
                this.confirm();
            }
            this.props.showPin = false;
        });
    },
});