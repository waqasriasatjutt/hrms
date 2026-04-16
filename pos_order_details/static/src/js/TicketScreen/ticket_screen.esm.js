/** @odoo-module */

import {OrderDetailsPopup} from "../Popups/order_details_popup.esm";
import {TicketScreen} from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import {makeAwaitable} from "@point_of_sale/app/store/make_awaitable_dialog";
import {patch} from "@web/core/utils/patch";

// Patch the TicketScreen prototype to add a new method. #T8407
patch(TicketScreen.prototype, {
    /**
     * New method for Opens the Order Details Popup for the selected order.
     * @param {Object} order - The order data to display in the popup. #T8407
     */
    async OpenOrderDetails(order) {
        await makeAwaitable(this.dialog, OrderDetailsPopup, {
            order: order,
        });
    },
});
