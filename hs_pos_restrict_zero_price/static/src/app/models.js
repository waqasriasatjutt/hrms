/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";

patch(PosStore.prototype, {

   async pay() {

        let self = this;
        let order = this.get_order();
        let lines = order.get_orderlines();
        let restrict_order = false;
        var product_names = ''
        if(this.env.services.pos.config.restrict_zero_price_line){
            if (order && lines.length > 0 ){
                lines.forEach(function (line){
                    if (line.get_display_price() == 0.00){
                       restrict_order = true;
                       product_names += '-' + line.full_product_name + "\n"
                    }
                });
            }
            else
            {
                 restrict_order = true;
            }
            if (restrict_order){
                if (product_names){
                   if(this.user.lang === 'fr_FR'){
                    this.dialog.add(AlertDialog, {
                    'title': _t("Produit à 0 prix"),
                    'body':  _t(' IMPOSSIBLE DE VALIDER AVEC UN PRIX 0. %s',product_names),
                 });
                   }else{
                    this.dialog.add(AlertDialog, {
                    'title': _t("Product With 0 Price"),
                    'body':  _t('You are not allowed to have the zero prices on the order line. %s',product_names),
                 });
                   }

                }
                else{
                 this.dialog.add(AlertDialog, {
                     title: _t("Zero quantity is not allowed"),
                     body: _t(
                    "Only a positive quantity is allowed for confirming the order."
                ),
            });
                }
            }
            else{
                super.pay();
            }
            }
              else{
                super.pay();
            }
    },

});