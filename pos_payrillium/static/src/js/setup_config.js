/** @odoo-module **/

import { ConfigLoader } from "@pos_payrillium/js/config_loader";
import { rpc } from "@web/core/network/rpc";
/**
 * Loads all Payrillium configuration for the POS.
 * @param {function} rpc - Odoo RPC service.
 * @returns {object} Object with all the required configuration.
 */
export async function loadPayrilliumConfig(posService) {
  try {
    const fullData = await ConfigLoader.getFullPaymentMethodData(rpc);
    const paymentMethodName = await ConfigLoader.getPaymentMethodName(rpc);
    const paymentMethodColor = await ConfigLoader.getPaymentMethodColor(rpc);
    const paymentMethodIcon = await ConfigLoader.getPaymentMethodIcon(rpc);
    const receivableAccountId = fullData.receivable_account_id;
    const paymentProviderId = fullData.payment_provider_id;
    const terminalId = await ConfigLoader.getTerminalFromSession(posService);
    // const terminalId = fullData.terminal_id;

    console.log("  Configuration loaded:", {
      name: paymentMethodName,
      color: paymentMethodColor,
      icon: paymentMethodIcon,
      paymentProviderId,
      receivableAccountId,
      terminalId,
    });

    return {
      name: paymentMethodName,
      color: paymentMethodColor,
      icon: paymentMethodIcon,
      receivableAccountId,
      paymentProviderId,
      terminalId,
    };
  } catch (error) {
    console.error("  Error loading configuration:", error);
    return null;
  }
}
