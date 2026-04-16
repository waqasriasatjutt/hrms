/** @odoo-module **/

import { LoginScreen } from "@point_of_sale/app/screens/login_screen/login_screen";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(LoginScreen.prototype, {
    get backBtnName() {
        if (this.pos.user.sbl_pos_config_id) {
            return _t("Logout");
        }
        return _t("Backend");
    }
});
