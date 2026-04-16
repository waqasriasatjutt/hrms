/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { ClosePosPopup } from "@point_of_sale/app/navbar/closing_popup/closing_popup";
import { useState, onWillStart } from "@odoo/owl";
import { formatMonetary } from "@web/views/fields/formatters";

patch(ClosePosPopup.prototype, {
    setup() {
        super.setup(...arguments);
        if (!this.state.multiPayment) {
            this.state.multiPayment = [];  // reactive array
        }

        onWillStart(async ()=>{

            await this._get_multi_payment_currency()
        })
    },
    async _get_multi_payment_currency(){
        try {
             let records = await this.orm.call("pos.payment",
                    "get_currency_amount",
                    [[],],
                {session_id : this.pos.pos_session.id}
            );
            this.state.multiPayment = records.map((rec) => {
                return {
                    ...rec,
                    price_total_formatted: formatMonetary(rec.currency_amount),
                };
            });
        } catch (error) {
            console.error("Error fetching multi-payment currencies:", error);
        }
    }


});