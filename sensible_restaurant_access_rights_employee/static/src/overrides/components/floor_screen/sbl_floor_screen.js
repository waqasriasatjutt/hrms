/** @odoo-module */

import { FloorScreen } from "@pos_restaurant/app/floor_screen/floor_screen";
import { patch } from "@web/core/utils/patch";
import { onMounted, useEffect } from "@odoo/owl";

patch(FloorScreen.prototype, {
    setup() {
        super.setup(...arguments);

        onMounted(() => {
            this.sblApplyFloorRestrictions();
        });

        useEffect(
            () => {
                this.sblApplyFloorRestrictions();
            },
            () => [this.state.selectedFloorId]
        );
    },

    /**
     * Returns the list of disabled floor IDs for the current employee.
     */
    get sblDisabledFloorIds() {
        const employee = this.pos.get_cashier();
        const disabledFloors = employee?.sbl_disabled_floor_ids;
        if (!disabledFloors || !Array.isArray(disabledFloors)) {
            return [];
        }
        return disabledFloors.map(fd => fd.id);
    },

    /**
     * Returns floors that are accessible to the current employee.
     */
    get sblAccessibleFloors() {
        const allFloors = this.pos.models["restaurant.floor"].getAll();
        const disabledIds = this.sblDisabledFloorIds;

        if (!disabledIds.length) {
            return allFloors;
        }
        return allFloors.filter((floor) => !disabledIds.includes(floor.id));
    },

    /**
     * Apply floor restrictions by hiding disabled floor buttons and
     * auto-selecting an accessible floor if needed.
     */
    sblApplyFloorRestrictions() {
        const disabledIds = this.sblDisabledFloorIds;
        const allFloors = this.pos.models["restaurant.floor"].getAll();

        // Update visibility of floor buttons
        const floorButtons = document.querySelectorAll(".floor-selector .button-floor");
        floorButtons.forEach((btn, index) => {
            if (allFloors[index]) {
                const floor = allFloors[index];
                btn.style.display = disabledIds.includes(floor.id) ? "none" : "";
            }
        });

        // If current floor is disabled, auto-select first accessible floor
        if (this.state.selectedFloorId && disabledIds.includes(this.state.selectedFloorId)) {
            const accessibleFloor = this.sblAccessibleFloors[0];
            if (accessibleFloor) {
                this.state.selectedFloorId = accessibleFloor.id;
                this.pos.currentFloor = accessibleFloor;
            }
        }

        // If no floor selected and accessible floors exist, select the first one
        if (!this.state.selectedFloorId && this.sblAccessibleFloors.length) {
            const firstAccessible = this.sblAccessibleFloors[0];
            this.state.selectedFloorId = firstAccessible.id;
            this.pos.currentFloor = firstAccessible;
        }
    },

    /**
     * Override selectFloor to prevent selecting disabled floors.
     */
    selectFloor(floor) {
        if (this.sblDisabledFloorIds.includes(floor.id)) {
            return;
        }
        super.selectFloor(floor);
    },
});
