/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { PayrilliumAPI } from "@pos_payrillium/js/api_service";

patch(PosOrder.prototype, {
  async add_product(product, options) {
    const result = await super.add_product(product, options);

    try {
      const rpc = this.env.services.rpc;
      // Try to get sessionId from pos service
      const posService = this.env?.services?.pos || this.pos;
      const sessionId = posService?.session?.id || null;
      await PayrilliumAPI.showBasket(this, null, sessionId);
    } catch (error) {
      console.error("Error synchronizing with terminal:", error);
    }

    return result;
  },
});
