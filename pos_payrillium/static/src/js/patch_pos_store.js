/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { PayrilliumAPI } from "@pos_payrillium/js/api_service";

console.log(" Patch deleteOrders in PosStore");

const _superDeleteOrders = PosStore.prototype.deleteOrders;

patch(PosStore.prototype, {
  setup() {
    super.setup(...arguments);
    this._posService = this.pos || this.env.services.pos;
  },

  async deleteOrders(orders, serverIds = []) {
    const result = await _superDeleteOrders.call(this, orders, serverIds);
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

    const order = this.get_order?.();
    try {
      const sessionId = this._posService.session?.id || null;
      if (order && order.get_orderlines?.().length) {
        await PayrilliumAPI.showBasket({ order }, null, sessionId);
      } else {
        await PayrilliumAPI.showEmptyBasket(null, sessionId);
      }
    } catch (error) {
      console.error("Payrillium: error synchronizing with terminal:", error);
    }
  },
});
