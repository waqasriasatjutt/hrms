/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { PayrilliumAPI } from "@pos_payrillium/js/api_service";
import { useService } from "@web/core/utils/hooks";
import { useBarcodeReader } from "@point_of_sale/app/barcode/barcode_reader_hook";

const _orig_barcodeProductAction =
  ProductScreen.prototype._barcodeProductAction;
const _orig_barcodeGS1Action = ProductScreen.prototype._barcodeGS1Action;

patch(ProductScreen.prototype, {
  setup() {
    super.setup(...arguments);
    this._posService = this.pos || this.env.services.pos;
  },

  async addProductToOrder(product) {
    console.log("Adding product to order:", product);
    await super.addProductToOrder(product);
    await this._syncBasketWithTerminal();
  },

  async _barcodeProductAction(code) {
    console.log("Barcode product action fired, code:", code);
    await _orig_barcodeProductAction.call(this, code);
    await this._syncBasketWithTerminal();
  },

  async _barcodeGS1Action(parsed_results) {
    console.log("Barcode GS1 action fired, parsed_results:", parsed_results);
    await _orig_barcodeGS1Action.call(this, parsed_results);
    await this._syncBasketWithTerminal();
  },

  async deleteOrders(orders) {
    const res = await super.deleteOrders?.call(this, orders);
    try {
      if (res) {
        const sessionId = this._posService.session?.id || null;
        await PayrilliumAPI.showEmptyBasket(null, sessionId);
      }
    } catch (e) {
      console.error("Payrillium cleanup after deleteOrders failed:", e);
    }
    return res;
  },

  async _syncBasketWithTerminal() {
    const terminal = this._posService.config.payrillium_terminal_serial;
    console.log("terminal", terminal);
    const isString = typeof terminal === "string";
    const hasTerminal = terminal && isString && terminal.length > 0;
    if (!hasTerminal) {
      console.log("No terminal assigned to session.");
      return;
    }
    const order = this.currentOrder;
    try {
      const sessionId = this._posService.session?.id || null;
      await PayrilliumAPI.showBasket(order, null, sessionId);
    } catch (error) {
      console.error(" Error synchronizing with terminal:", error);
    }
  },
});
