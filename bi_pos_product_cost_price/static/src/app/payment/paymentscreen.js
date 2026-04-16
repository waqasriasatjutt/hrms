/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { AlertDialog, ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

import { _t } from "@web/core/l10n/translation";

patch(PaymentScreen.prototype, {
   setup() {
        super.setup();
    
    },
    get currentOrder() {
        return this.pos.get_order();
    },
    async validateOrder(isForceValidate) {
       
        this.numberBuffer.capture();
        if (this.pos.config.cash_rounding) {
            if (!this.pos.get_order().check_paymentlines_rounding()) {
                this.popup.add(ErrorPopup, {
                    title: _t("Rounding error in payment lines"),
                    body: _t(
                        "The amount of your payment lines must be rounded to validate the transaction."
                    ),
                });
                return;
            }
        }
        if (await this._isOrderValid(isForceValidate)) {
            // remove pending payments before finalizing the validation
            for (const line of this.paymentLines) {
                if (!line.is_done()) {
                    this.currentOrder.remove_paymentline(line);
                }
                if(this.env.services.pos.config.restrict_sale_below_cost){
                   
                    var product_name = [];
                    var error = ' ';
                    for(let order_line of this.env.services.pos.get_order().lines) {
                        if(order_line.product_id.lst_price < order_line.product_id.standard_price) {
                            var flag = true;
                            product_name.push(order_line.product_id.display_name)
                        }
                    }
                    for(let a of product_name){
                        error += a + "\n";
                    }
                    if(flag == true){
                        this.dialog.add(AlertDialog, {
                            title:_t('Price Restricted'),
                            body: error,
                        });
                        flag = false;
                        return;
                    }
            }
            if(flag == false){
                await this._finalizeValidation();
            }
        
            }
            await this._finalizeValidation();
        }
    },
   
});