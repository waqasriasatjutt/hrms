/** @odoo-module **/

import { OrderSummary } from "@point_of_sale/app/screens/product_screen/order_summary/order_summary";
import { PayrilliumAPI } from "@pos_payrillium/js/api_service";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

patch(OrderSummary.prototype, {
  setup() {
    super.setup(...arguments);
    this.orm = useService("orm");
    this._posService = this.pos || this.env.services.pos;
  },

  async updateSelectedOrderline(props) {
    const result = await super.updateSelectedOrderline(props);
    console.log(" Orderline :", this.currentOrder.get_selected_orderline());
    await this._syncBasketWithTerminal();
    return result;
  },

  async _syncBasketWithTerminal() {
    const terminal = this._posService.config.payrillium_terminal_serial;
    const isString = typeof terminal === "string";
    const hasTerminal = terminal && isString && terminal.length > 0;
    if (!hasTerminal) {
      console.log("No terminal assigned to session.");
      return;
    }
    try {
      console.log(" Synchronizing basket with terminal...");
      const order = this.currentOrder;
      const sessionId = this._posService.session?.id || null;
      await PayrilliumAPI.showBasket(order, null, sessionId);
      console.log(" Terminal updated with current products");
    } catch (error) {
      console.error(" Error synchronizing with terminal:", error);
    }
  },
});
