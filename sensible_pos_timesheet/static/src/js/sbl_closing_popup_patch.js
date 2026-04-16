/** @odoo-module **/

import { ClosePosPopup } from "@point_of_sale/app/navbar/closing_popup/closing_popup";
import { patch } from "@web/core/utils/patch";

patch(ClosePosPopup.prototype, {
    async closeSession() {
        // Check if timesheet is enabled and stop timer + create check-out before closing session
        if (this.pos.config?.sbl_create_timesheet) {
            try {
                // Stop timer widget
                if (window.sblTimerWidget) {
                    window.sblTimerWidget.sbl_stop_timer();
                }

                // Create attendance check-out
                const checkOutResult = await this.pos.data.call(
                    'pos.session',
                    'sbl_create_attendance_checkout',
                    [this.pos.session.id]
                );

                if (checkOutResult.status === 'error') {
                    // Show notification to user
                    this.pos.notification.add(
                        checkOutResult.message || 'Failed to create attendance checkout',
                        { type: 'danger' }
                    );
                }
            } catch (error) {
                // Show notification to user
                this.pos.notification.add(
                    'Error creating attendance checkout: ' + (error.message || error),
                    { type: 'danger' }
                );
            }
        }

        // Call parent closeSession method
        return await super.closeSession();
    }
});