/** @odoo-module **/

import { OpeningControlPopup } from "@point_of_sale/app/store/opening_control_popup/opening_control_popup";
import { patch } from "@web/core/utils/patch";

patch(OpeningControlPopup.prototype, {
    async confirm() {
        // Call parent confirm method first
        const result = await super.confirm();

        // Check if timesheet is enabled and start timer + create check-in
        if (this.pos.config?.sbl_create_timesheet) {
            try {
                // Start timer widget
                if (window.sblTimerWidget) {
                    window.sblTimerWidget.sbl_start_timer();
                }

                // Create attendance check-in
                const checkInResult = await this.pos.data.call(
                    'pos.session',
                    'sbl_create_attendance_checkin',
                    [this.pos.session.id]
                );

                if (checkInResult.status === 'error') {
                    // Stop timer if it was started
                    if (window.sblTimerWidget) {
                        window.sblTimerWidget.sbl_stop_timer();
                    }

                    // Show notification to user
                    this.pos.notification.add(
                        checkInResult.message || 'Failed to create attendance record',
                        { type: 'danger' }
                    );
                }
            } catch (error) {
                // Stop timer if it was started
                if (window.sblTimerWidget) {
                    window.sblTimerWidget.sbl_stop_timer();
                }

                // Show notification to user
                this.pos.notification.add(
                    'Error creating attendance record: ' + (error.message || error),
                    { type: 'danger' }
                );
            }
        }

        return result;
    }
});