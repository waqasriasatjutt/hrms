/** @odoo-module **/

import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { patch } from "@web/core/utils/patch";
import { SblPosTimerWidget } from "./sbl_pos_timer_widget";

patch(Navbar, {
    components: { ...Navbar.components, SblPosTimerWidget },
});