/** @odoo-module **/

import { UserMenu } from "@web/webclient/user_menu/user_menu";
import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";

const userMenuRegistry = registry.category("user_menuitems");

patch(UserMenu.prototype, {
    setup() {
        super.setup();
        userMenuRegistry.remove("odoo_account");
        userMenuRegistry.remove("support");
        userMenuRegistry.remove("documentation");


//        userMenuRegistry.remove("shortcuts");
//        userMenuRegistry.remove("separator");
        userMenuRegistry.remove("profile");
//        userMenuRegistry.remove("log_out");
//        userMenuRegistry.remove("shortcuts");
//        userMenuRegistry.remove("separator");
        userMenuRegistry.remove("install_pwa");
    },
});
