/** @odoo-module **/

import { Component, onMounted, onWillUnmount, useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";

export class SblPosTimerWidget extends Component {
    static template = "sensible_pos_timesheet.SblPosTimerWidget";
    static props = {};

    setup() {
        this.pos = usePos();
        this.state = useState({
            sbl_elapsed_time: 0,
            sbl_is_active: false,
            sbl_timer_display: "00:00:00",
        });

        this.sbl_start_time = null;
        this.sbl_timer_interval = null;
        this.sbl_check_interval = null;

        onMounted(() => {
            this.sbl_restore_timer_state();

            // Expose widget globally for testing
            window.sblTimerWidget = this;
        });

        onWillUnmount(() => {
            if (this.sbl_timer_interval) {
                clearInterval(this.sbl_timer_interval);
            }
            if (this.sbl_check_interval) {
                clearInterval(this.sbl_check_interval);
            }
            this.sbl_save_timer_state();
        });
    }

    sbl_restore_timer_state() {
        const session = this.pos.session || this.pos.pos_session;
        if (!session) return;

        // Create a unique key for this session
        const sessionKey = `sbl_timer_${session.id}`;
        const savedState = localStorage.getItem(sessionKey);

        if (savedState) {
            try {
                const state = JSON.parse(savedState);
                this.sbl_start_time = new Date(state.start_time);
                this.state.sbl_is_active = state.is_active;

                if (this.state.sbl_is_active) {
                    // Start timer display update
                    this.sbl_update_timer_display();
                    this.sbl_timer_interval = setInterval(() => {
                        this.sbl_update_timer_display();
                    }, 1000);
                }
            } catch (e) {
                localStorage.removeItem(sessionKey);
            }
        }
    }

    sbl_save_timer_state() {
        const session = this.pos.session || this.pos.pos_session;
        if (!session || !this.sbl_start_time) return;

        const sessionKey = `sbl_timer_${session.id}`;
        const state = {
            start_time: this.sbl_start_time.toISOString(),
            is_active: this.state.sbl_is_active
        };

        localStorage.setItem(sessionKey, JSON.stringify(state));
    }

    sbl_start_timer() {
        if (this.state.sbl_is_active) {
            return;
        }

        const session = this.pos.session || this.pos.pos_session;
        // Start timer
        this.sbl_start_time = session?.start_at ? new Date(session.start_at) : new Date();
        this.state.sbl_is_active = true;

        // Update display immediately and then every second
        this.sbl_update_timer_display();
        this.sbl_timer_interval = setInterval(() => {
            this.sbl_update_timer_display();
        }, 1000);

        // Save state for persistence
        this.sbl_save_timer_state();
    }

    sbl_stop_timer() {
        if (!this.state.sbl_is_active) {
            return;
        }

        if (this.sbl_timer_interval) {
            clearInterval(this.sbl_timer_interval);
            this.sbl_timer_interval = null;
        }
        this.state.sbl_is_active = false;
        this.state.sbl_timer_display = "00:00:00";

        // Clear localStorage for this session
        const session = this.pos.session || this.pos.pos_session;
        if (session) {
            const sessionKey = `sbl_timer_${session.id}`;
            localStorage.removeItem(sessionKey);
        }
    }

    sbl_update_timer_display() {
        if (!this.state.sbl_is_active || !this.sbl_start_time) {
            return;
        }

        const now = new Date();
        const elapsed_seconds = Math.floor((now - this.sbl_start_time) / 1000);
        this.state.sbl_elapsed_time = elapsed_seconds;

        const hours = Math.floor(elapsed_seconds / 3600);
        const minutes = Math.floor((elapsed_seconds % 3600) / 60);
        const seconds = elapsed_seconds % 60;

        // Format with blinking separator
        const separator = seconds % 2 === 0 ? ":" : " ";
        this.state.sbl_timer_display = `${hours.toString().padStart(2, '0')}${separator}${minutes.toString().padStart(2, '0')}${separator}${seconds.toString().padStart(2, '0')}`;
    }

    get sbl_should_show() {
        const session = this.pos.session || this.pos.pos_session;
        return this.pos.config && this.pos.config.sbl_create_timesheet && session && session.state === 'opened';
    }

    get sbl_timer_class() {
        return this.state.sbl_is_active ? 'sbl-timer-active' : 'sbl-timer-inactive';
    }


}