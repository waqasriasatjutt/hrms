/** @odoo-module **/

import { ConfigLoader } from "@pos_payrillium/js/config_loader";
import { rpc } from "@web/core/network/rpc";
console.log("  POS Payrillium - API Service LOADING");

// Helper function to get terminal info and log it
async function _logTerminalInfo(sessionId, actionName) {
  if (sessionId) {
    try {
      const result = await rpc("/payrillium/session/terminal", {
        sessionId: sessionId,
      });
      if (result.success && result.terminal) {
        console.log(`🔌 [${actionName}] Sending request to Terminal:`, {
          id: result.terminal.id,
          name: result.terminal.name,
          serial: result.terminal.serial,
          sessionId: sessionId,
        });
        return result.terminal;
      }
    } catch (error) {
      console.warn(`⚠️ [${actionName}] Could not get terminal info:`, error);
    }
  } else {
    console.warn(
      `⚠️ [${actionName}] No sessionId provided, using fallback terminal lookup`
    );
  }
  return null;
}

export const PayrilliumAPI = {
  async showBasket(input, executionId = null, sessionId = null) {
    const order = input?.pos_order_id || input?.order || input;

    if (!order) {
      console.error("Invalid order input");
      return { success: false, message: "Invalid order input" };
    }

    const lines =
      order.get_orderlines?.() ||
      order.getOrderReceiptEnv?.()?.orderlines ||
      order.orderlines?.models ||
      order.orderlines ||
      [];

    if (!Array.isArray(lines)) {
      console.error("Could not resolve orderlines");
      return { success: false, message: "Invalid orderlines" };
    }

    console.log(lines, "lines");
    const imageBaseUrl = await ConfigLoader.getImageBaseUrl();
    console.log(imageBaseUrl, "imageBaseUrl");

    const products = lines.map((line) => ({
      id: line.product_id.id,
      sale_upc_code: line.product_id.barcode || "N/A",
      upc_code: line.product_id.barcode || "N/A",
      image: `${imageBaseUrl}/image/${line.product_id.id}` || "",
      name: line.product_id.display_name,
      qty: `${line.qty}`,
      price: `${line.get_unit_price().toFixed(2)}`,
      total: `${line.get_display_price().toFixed(2)}`,
      group_name: "DEFAULT",
    }));

    const discount = lines.reduce((acc, line) => {
      console.log(line.get_discount(), "line");

      const line_total = line.get_unit_price() * line.qty;
      return acc + (line_total * line.get_discount()) / 100;
    }, 0);
    console.log(discount, "discount");

    const payload = {
      products,
      currency: "USD",
      subtotal: order.get_total_without_tax().toFixed(2),
      tax: order.get_total_tax().toFixed(2),
      discount: discount.toFixed(2),
      items: `${lines.length}`,
      total: order.get_total_with_tax().toFixed(2),
      cash_discount: "0.00",
      non_cash_adjustment: "0.00",
      total_after_cash_discount: order.get_total_with_tax().toFixed(2),
      cash_discount_config_active: true,
      transaction_type: "sale",
    };
    console.log("  Starting showBasket request");

    try {
      await _logTerminalInfo(sessionId, "showBasket");
      const response = await rpc("/payrillium/proxy/basket", {
        kwargs: { ...payload, executionId, sessionId },
      });

      if (response.status === "error") {
        console.error("Basket request failed:", response.message);
        throw new Error(response.message);
      }

      return response;
    } catch (error) {
      console.error("  Error Error showBasket request:", error);
      return { status: "error", message: error.message };
    }
  },
  async showEmptyBasket(executionId = null, sessionId = null) {
    const payload = {
      products: [],
      currency: "USD",
      subtotal: "0.00",
      tax: "0.00",
      discount: "0.00",
      items: "0",
      total: "0.00",
      cash_discount: "0.00",
      non_cash_adjustment: "0.00",
      total_after_cash_discount: "0.00",
      cash_discount_config_active: true,
      transaction_type: "sale",
    };

    try {
      await _logTerminalInfo(sessionId, "showEmptyBasket");
      const response = await rpc("/payrillium/proxy/basket", {
        kwargs: { ...payload, executionId, sessionId },
      });
      if (response.status === "error") {
        console.error("Basket request failed:", response.message);
        throw new Error(response.message);
      }
      return response;
    } catch (error) {
      console.error("  Error during showEmptyBasket request:", error);
      return { status: "error", message: error.message };
    }
  },

  async requestCardType(executionId = null, sessionId = null) {
    try {
      await _logTerminalInfo(sessionId, "requestCardType");
      const response = await rpc("/payrillium/proxy/card", {
        kwargs: { data: "", executionId, sessionId },
      });
      return response;
    } catch (error) {
      console.error("  Error during requestCardType:", error);
      return { success: false, message: error.message };
    }
  },

  async showTipSelection(paymentLine, executionId = null, sessionId = null) {
    const amount = paymentLine.order.get_total_with_tax();
    const tipOptions = ["1", "2", "5", "Custom", "No Tip"];
    let tipAmount = 0;

    try {
      const payload = {
        title: "Select Tip",
        menu: tipOptions,
        amount,
      };
      await _logTerminalInfo(sessionId, "showTipSelection");
      const tipResult = await rpc("/payrillium/proxy/tip", {
        kwargs: { ...payload, executionId, sessionId },
      });
      if (tipResult.status === "error") {
        console.error("Tip request failed:", tipResult.message);
        throw new Error(tipResult.message);
      }

      const resultType = tipResult?.data?.type;
      const resultData = tipResult?.data?.data;

      if (resultType?.includes("TipResultCustom")) {
        tipAmount = parseFloat(resultData?.value || 0);
      } else if (resultType?.includes("TipResultOption")) {
        const index = resultData?.selection;
        const option = tipOptions[index];
        const parsed = parseFloat(option);
        if (!isNaN(parsed)) tipAmount = parsed;
      }
    } catch (error) {
      console.error("  Error during tip selection:", error);
    }

    return tipAmount;
  },

  async capturePayment(
    paymentLine,
    cardType,
    tipAmount,
    paymentRef,
    executionId = null,
    sessionId = null
  ) {
    const payload = {
      cardType: cardType || "CREDIT",
      payment_id: paymentRef,
      amount: paymentLine.pos_order_id.get_total_with_tax().toFixed(2),
      tip: tipAmount ? tipAmount.toFixed(2) : "",
      tokenizeCard: true,
    };

    try {
      await _logTerminalInfo(sessionId, "capturePayment");
      const response = await rpc("/payrillium/payment/auth", {
        kwargs: { ...payload, executionId, sessionId },
      });
      if (response.status === "error") {
        console.error("Basket request failed:", response.message);
        throw new Error(response.message);
      }
      return response;
    } catch (error) {
      console.error("  Error during capturePayment:", error);
      return { status: "error", message: error.message };
    }
  },

  async captureCreditPayment(payload, executionId = null, sessionId = null) {
    try {
      await _logTerminalInfo(sessionId, "captureCreditPayment");
      const response = await rpc("/payrillium/payment/capture", {
        kwargs: { ...payload, executionId, sessionId },
      });
      if (response.status === "error") {
        console.error("Basket request failed:", response.message);
        throw new Error(response.message); // force the catch
      }
      return response;
    } catch (error) {
      console.error("  Error during captureCreditPayment:", error);
      return { success: false, message: error.message };
    }
  },

  async authReversal(payload, executionId = null, sessionId = null) {
    try {
      await _logTerminalInfo(sessionId, "authReversal");
      const response = await rpc("/payrillium/payment/auth_reversal", {
        kwargs: { ...payload, executionId, sessionId },
      });
      if (response.status === "error") {
        console.error("Basket request failed:", response.message);
        throw new Error(response.message); // force the catch
      }
      return response;
    } catch (error) {
      console.error("  Error during authReversal:", error);
      return { success: false, message: error.message };
    }
  },

  async refundDebit(payload, executionId = null, sessionId = null) {
    try {
      await _logTerminalInfo(sessionId, "refundDebit");
      const response = await rpc("/payrillium/payment/refund_debit", {
        kwargs: { ...payload, executionId, sessionId },
      });
      if (response.status === "error") {
        console.error("refund request failed:", response.message);
        throw new Error(response.message);
      }
      return response;
    } catch (error) {
      console.error("  Error during refundDebit:", error);
      return { success: false, message: error.message };
    }
  },

  async refundCredit(payload, executionId = null, sessionId = null) {
    try {
      await _logTerminalInfo(sessionId, "refundCredit");
      const response = await rpc("/payrillium/payment/refund", {
        kwargs: { ...payload, executionId, sessionId },
      });
      if (response.status === "error") {
        console.error("refund request failed:", response.message);
        throw new Error(response.message);
      }
      return response;
    } catch (error) {
      console.error("  Error during refundCredit:", error);
      return { success: false, message: error.message };
    }
  },
  async refundTokenize(payload, executionId = null, sessionId = null) {
    try {
      await _logTerminalInfo(sessionId, "refundTokenize");
      const response = await rpc("/payrillium/refund_tokenize", {
        kwargs: { ...payload, executionId, sessionId },
      });
      if (response.status === "error") {
        console.error("refund request failed:", response.message);
        throw new Error(response.message);
      }
      return response;
    } catch (error) {
      console.error("  Error during refundTokenize:", error);
      return { success: false, message: error.message };
    }
  },

  async send_payment_request(cid, amount, executionId = null) {
    try {
      const response = await this.showBasket(amount, executionId);
      if (response.status === "error") throw new Error(response.message);

      return {
        cid,
        payment_status: response.status === "success" ? "done" : "retry",
        transaction_id: response.transaction_id || null,
        message: response.message,
      };
    } catch (error) {
      console.error("  Error in send_payment_request:", error);
      return {
        cid,
        payment_status: "retry",
        message: error.message,
      };
    }
  },
};

console.log("  POS Payrillium - API Service READY");
