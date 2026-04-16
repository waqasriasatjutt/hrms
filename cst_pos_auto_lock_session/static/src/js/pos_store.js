/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";


patch(PosStore.prototype, {
    async setup() {
        await super.setup(...arguments);

        if (this.config.auto_lock_enabled) {
            this.lastActivityTime = Date.now();
            this.setActivityListeners();
            this.startAutoLockTimer();
        }
    },

    setActivityListeners() {
        if (this._activityListenersSet) return;
        this._activityListenersSet = true;

        this._idleTimerSetter = this.resetActivityTimer.bind(this);

        for (const event of [
            "mousemove", "mousedown", "touchstart",
            "touchend", "touchmove", "click",
            "scroll", "keypress"
        ]) {
            window.addEventListener(event, this._idleTimerSetter, { passive: true });
        }
    },

    resetActivityTimer() {
        this.lastActivityTime = Date.now();
    },

    startAutoLockTimer() {
        if (this._autoLockInterval) {
            clearInterval(this._autoLockInterval);
        }

        this._autoLockInterval = setInterval(() => {
            if (!this.config.auto_lock_enabled || !this.get_cashier()) {
                return;
            }

            const idleTime = Date.now() - this.lastActivityTime;
            const lockTimeMs = Math.max(
                (this.config.auto_lock_time || 0) * 1000,
                1000
            );

            if (
                idleTime >= lockTimeMs &&
                this.env.services.pos.ui.screen !== "LoginScreen"
            ) {
                debugger;
                this.showLoginScreen();
                this.resetActivityTimer();
            }
        }, 3000);
    },

    destroy() {
        if (this._autoLockInterval) {
            clearInterval(this._autoLockInterval);
        }
        super.destroy?.();
    },
});
