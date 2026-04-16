/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { _t } from "@web/core/l10n/translation";
import { rpc } from "@web/core/network/rpc";
import { ask } from "@point_of_sale/app/store/make_awaitable_dialog";
/**
 * Adds a product line to the current order, with an additional check for age-restricted products.
 * If the product has an age restriction, a dialog will appear asking for confirmation to proceed.
 * If the user approves, the product is added to the order. Otherwise, the action is canceled.**/

patch(PosStore.prototype, {
    async addLineToCurrentOrder(vals, opt = {}, configure = true) {
       var product = vals.product_id.id
       var age_restrict = vals.product_id.is_age_restrict
       if (age_restrict){
             const confirmed = await ask(this.dialog, {
              title: _t("Age Restricted Product!"),
              body: _t("Attention!!This product is under the age restricted category."),
              cancelLabel: _t("Reject"),
              confirmLabel: _t("Approve"),
            });
            if (confirmed) {
               return super.addLineToCurrentOrder(vals, opt, configure)
            }
        }else{
        return super.addLineToCurrentOrder(vals, opt, configure);}
    },
        });
