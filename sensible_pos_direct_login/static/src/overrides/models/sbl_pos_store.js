import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
    redirectToBackend() {
        let route = "/odoo/action-point_of_sale.action_client_pos_menu";
        if (this.session.user_id && this.session.user_id.sbl_pos_config_id) {
            route = '/web/session/logout';
        }
        window.location = route;
    }
});
