/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { useService } from "@web/core/utils/hooks";

/**
 * Ensure ControlButtons setup is properly called to avoid null context issues
 * This fixes issues with pos_qz module's onClickPrintNote
 */
patch(ControlButtons.prototype, {
    setup() {
        super.setup();
        // Ensure all services are available - use useService if not already set
        try {
            if (!this.dialog && this.env?.services?.dialog) {
                this.dialog = this.env.services.dialog;
            }
            if (!this.notification && this.env?.services?.notification) {
                this.notification = this.env.services.notification;
            }
            if (!this.hardwareProxy && this.env?.services?.hardware_proxy) {
                this.hardwareProxy = this.env.services.hardware_proxy;
            }
        } catch (e) {
            console.warn("ControlButtons setup patch: Could not set services", e);
        }
    },
});