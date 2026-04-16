/** @odoo-module **/

export async function showAmountOnTerminal(
  payrilliumAPI,
  paymentLine,
  executionId,
  sessionId = null
) {
  const result = await payrilliumAPI.showBasket(paymentLine, executionId, sessionId);
  await new Promise((resolve) => setTimeout(resolve, 2000));
  return result;
}

export async function selectCardType(payrilliumAPI, executionId, sessionId = null) {
  return await payrilliumAPI.requestCardType(executionId, sessionId);
}

export async function handleTip(
  payrilliumAPI,
  paymentLine,
  posService,
  executionId,
  sessionId = null
) {
  if (!posService.config.iface_tipproduct) {
    return {
      success: true,
      data: {
        state: "SUCCESS",
        data: {
          tipAmount: 0,
          message: "Tips not enabled",
        },
      },
    };
  }

  const result = await payrilliumAPI.showTipSelection(paymentLine, executionId, sessionId);

  const tipAmount = result.data?.data?.tipAmount;
  if (tipAmount > 0) {
    paymentLine.order.set_tip(tipAmount);
    const newTotal = paymentLine.order.get_total_with_tax();
    paymentLine.set_amount(newTotal);
  }

  return result;
}

export async function authorizePayment(
  payrilliumAPI,
  paymentLine,
  cardType,
  tipAmount,
  paymentRef,
  executionId,
  sessionId = null
) {
  const result = await payrilliumAPI.capturePayment(
    paymentLine,
    cardType,
    tipAmount,
    paymentRef,
    executionId,
    sessionId
  );
  return result;
}

export async function handleAuthorizationFailure(
  payrilliumAPI,
  paymentLine,
  cardType,
  result,
  paymentRef,
  executionId,
  transactionId,
  sessionId = null
) {
  if (cardType === "CREDIT") {
    try {
      await payrilliumAPI.authReversal({
        payment_id: `${paymentRef}rv`,
        transaction_id: transactionId,
        totalAmount: paymentLine.pos_order_id.get_total_with_tax().toFixed(2),
        reason: "",
        executionId,
      }, executionId, sessionId);

      return {
        success: true,
        data: {
          state: "REVERSED",
          data: {
            message: "Payment authorization reversed",
          },
        },
      };
    } catch (error) {
      return {
        success: false,
        data: {
          state: "ERROR",
          data: {
            message: error.message || "Error reversing authorization",
            type: "ERROR",
            originalError: error,
          },
        },
      };
    }
  }

  paymentLine.set_payment_status("retry");
  return {
    success: false,
    data: {
      state: "RETRY",
      data: {
        message: "Payment needs retry",
        type: "RETRY",
      },
    },
  };
}

export async function captureCredit(
  payrilliumAPI,
  paymentLine,
  paymentRef,
  transactionId,
  executionId,
  message,
  sessionId = null
) {
  const entryMode = message?.entryMode?.toUpperCase?.();
  const emvTags = ["CONTACT", "CONTACTLESS"].includes(entryMode)
    ? message?.emvTags || ""
    : undefined;

  const payload = {
    payment_id: `${paymentRef}c`,
    amount: paymentLine.pos_order_id.get_total_with_tax().toFixed(2),
    transaction_id: transactionId,
    ...(emvTags !== undefined && { emv_tags: emvTags }),
  };

  console.log("payload", payload);

  const result = await payrilliumAPI.captureCreditPayment(payload, executionId, sessionId);
  return result;
}

export async function processRefund(payrilliumAPI, params) {
  const {
    cardType,
    paymentId,
    transaction_id,
    amount,
    executionId,
    terminalId,
    tokenCardId,
    sessionId,
  } = params;

  console.log("Processing refund with parameters:", {
    cardType,
    paymentId,
    transaction_id,
    amount,
    executionId,
    tokenCardId,
  });

  const basePayload = {
    payment_id: `${paymentId}r`,
    transaction_id,
  };
  // ojo cardtype now is tokenize card

  let result;

  if (cardType === "CARD_PAYMENT") {
    // Tokenize card refund
    result = await payrilliumAPI.refundTokenize(
      { ...basePayload, amount, token_card_id: tokenCardId },
      executionId || null,
      sessionId || null
    );
  } else if (cardType === "CREDIT") {
    // Credit card refund
    result = await payrilliumAPI.refundCredit(
      { ...basePayload, amount },
      executionId || null,
      sessionId || null
    );
  } else {
    // Debit card refund (default)
    result = await payrilliumAPI.refundDebit(
      {
        ...basePayload,
        totalAmount: amount,
        tips: "",
        cashback: "",
      },
      executionId || null,
      sessionId || null
    );
  }

  return result;
}
