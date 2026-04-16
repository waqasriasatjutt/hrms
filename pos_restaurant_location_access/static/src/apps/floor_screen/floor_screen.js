/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { FloorScreen } from "@pos_restaurant/app/floor_screen/floor_screen";

patch(FloorScreen.prototype, {
    setup() {
        super.setup();
    },

    get filtred_floors() {
        let floors = this.pos.models['restaurant.floor'].getAll();
        const cashier = this.pos.get_cashier();
        if (cashier && cashier._role === 'cashier') {
            const floor_ids = (cashier.floor_ids || []).map(f => f.id);
            floors = floors.filter(floor => floor_ids.includes(floor.id));
        }
        if (floors.length && !floors.includes(this.activeFloor)) {
            this.state.selectedFloorId = floors[0].id;
        }
        return floors;
    },
});
