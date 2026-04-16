/** @odoo-module **/

import { parseEMVData } from "@pos_payrillium/js/utils";
import { ARC_MEANING, CARD_VENDOR, mapCVMCode } from "./utils";
import { rpc } from "@web/core/network/rpc";
export function buildPaymentReference() {
  const timestamp = Date.now();
  const random = Math.floor(Math.random() * 1000)
    .toString()
    .padStart(3, "0");
  return `${timestamp}${random}`;
}

export function isAuthorizationSuccessful(result) {
  return result.success === true && result.data?.state === "SUCCESS_AUTH";
}

export function getErrorMessage(result) {
  return result.data?.data?.message?.error || "Payment not approved";
}

export function storeTransactionMetadata(
  currentOrder,
  paymentLine,
  transactionId,
  message,
  cardType,
  parsedEMV,
  paymentProviderId
) {
  const responseCode = message.responseCode || "N/A";
  console.log("responseCode", message);

  const responseCodeMeaning = ARC_MEANING[responseCode] || "N/A";
  const cvm = mapCVMCode(message.cvm) || "N/A";
  currentOrder.set_extra_payment_data({
    cardType: cardType || "N/A",
    approvalCode: message.approvalCode || "N/A",
    cardVendor: message.cardVendor || "N/A",
    cardNumber: message.cardNumber || "N/A",
    transactionId: message.transactionId || "N/A",
    terminalId:
      message.rawBody?.pointOfSaleInformation?.terminalId ||
      message.terminalId ||
      "N/A",
    entryMode: message.entryMode || "N/A",
    date: message.date
      ? message.date.replace("T", " ").replace("Z", "")
      : "N/A",
    status: message.status || "N/A",
    CVM: cvm || "N/A",
    responseCode: responseCode || "N/A",
    responseCodeMeaning: responseCodeMeaning || "N/A",
    ...parsedEMV,
  });
  paymentLine.set_payment_status("done");
  paymentLine.transaction_id = transactionId;
  paymentLine.provider_id = paymentProviderId;
}

export async function findRefundedOrderLine(order) {
  const refundedLine = order
    .get_orderlines()
    .find((ol) => Boolean(ol.refunded_orderline_id));

  console.log(refundedLine, "refundedLine");

  if (!refundedLine) {
    throw new Error("Refunded product not found.");
  }

  const refundedLineId =
    refundedLine.refunded_orderline_id?.id ||
    refundedLine.refunded_orderline_id;

  if (!refundedLineId) {
    throw new Error("Refunded line ID not found.");
  }

  const [refundedLineBackend] = await rpc("/web/dataset/call_kw", {
    model: "pos.order.line",
    method: "read",
    args: [[refundedLineId], ["id", "order_id"]],
    kwargs: {},
  });

  if (!refundedLineBackend) {
    throw new Error("Refunded line backend not found.");
  }

  return {
    id: refundedLineBackend.id,
    order_id: refundedLineBackend.order_id?.[0] || null,
  };
}

export async function getOriginalTransaction(orderId) {
  // 1. Get the payment from pos.payment
  const payments = await rpc("/web/dataset/call_kw", {
    model: "pos.payment",
    method: "search_read",
    args: [[["pos_order_id", "=", orderId]], ["transaction_id"]],
    kwargs: {},
  });

  const transaction_id = payments?.[0]?.transaction_id;
  if (!transaction_id) {
    throw new Error("Transaction ID for the original order not found");
  }
  console.log("transaction_id", transaction_id);
  // 2. Get the transaction details
  const [trx] = await rpc("/web/dataset/call_kw", {
    model: "payment.transaction",
    method: "search_read",
    args: [
      [["provider_reference", "=", transaction_id]],
      ["card_type", "provider_reference", "reference", "payrillium_card_token"],
    ],
    kwargs: {},
  });

  if (!trx) {
    throw new Error("Original transaction details not found");
  }

  return {
    cardType: trx.card_type,
    tokenCardId: trx.payrillium_card_token,
    reference: trx.reference,
    transaction_id: transaction_id,
  };
}

export function prepareRefundData(result, originalData) {
  console.log("prepareRefundData - Input result:", result);

  const message = result.data?.data?.message || {};
  const request = result.data?.data?.request || {};
  const processor =
    originalData.cardType === "CREDIT"
      ? message.rawResponse.processorInformation
      : message.processorInformation;

  const emvRawTags =
    message.emvTags || request?.pointOfSaleInformation?.emv?.tags || "";

  const parsed = parseEMVData(emvRawTags);
  console.log("prepareRefundData - Parsed EMV data:", parsed);
  console.log(message, "message");
  console.log(message.rawResponse, "message.rawResponse");

  const submitTime =
    message?.submitTimeUtc || message?.rawResponse?.submitTimeUtc;
  const formattedDate = (submitTime ? submitTime : new Date().toISOString())
    .replace("T", " ")
    .replace("Z", "");

  let refundData = {};

  if (originalData.cardType !== "card_payment") {
    refundData = {
      transactionId: originalData?.transaction_id,
      // cardType:
      //   result?.data?.data?.request?.paymentInformation?.paymentType?.subTypeName?.toUpperCase() ||
      //   originalData?.cardType ||
      //   "N/A",
      // cardNumber: "****",
      // entryMode:
      //   result?.data?.data?.request?.pointOfSaleInformation?.entryMode?.toUpperCase() ||
      //   "UNKNOWN",
      // approvalCode:
      //   result?.data?.data?.message?.rawResponse?.processorInformation
      //     ?.approvalCode || "N/A",
      // cardVendor: "N/A",
      date:
        result?.data?.data?.message?.rawResponse?.submitTimeUtc ||
        result?.data?.data?.message?.submitTimeUtc ||
        formattedDate,
      status:
        result?.data?.data?.message?.status ||
        result?.data?.data?.message?.rawResponse?.status ||
        result?.data?.state ||
        "N/A",
      isRefund: true,
      originalTransactionId: originalData?.transaction_id,
      terminalId:
        originalData?.terminalId ||
        result?.serial ||
        result?.data?.data?.message?.rawResponse?.clientReferenceInformation
          ?.code ||
        "N/A",
      ...parsed,
    };
  } else {
    //tokenize card
    refundData = {
      transactionId: originalData.transaction_id,
      // cardType:
      //   result?.data?.refund_data?.raw?.data?.metadata?.paymentInformation?.card
      //     ?.type ||
      //   originalData.cardType ||
      //   "N/A",
      // cardNumber: "****",
      // entryMode: "UNKNOWN",
      // approvalCode:
      //   result?.data?.refund_data?.raw?.data?.metadata?.processorInformation
      //     ?.approvalCode || "N/A",
      // cardVendor:
      //   CARD_VENDOR[
      //     result?.data?.refund_data?.raw?.data?.metadata?.paymentInformation
      //       ?.tokenizedCard?.type
      //   ] || "N/A",
      date:
        result?.data?.refund_data?.raw?.data?.metadata?.submitTimeUtc ||
        formattedDate,
      status:
        result?.data?.refund_data?.raw?.data?.metadata?.status ||
        result?.data?.refund_data?.status ||
        "N/A",
      isRefund: true,
      originalTransactionId: originalData.transaction_id,
      terminalId:
        originalData.terminalId ||
        result?.data?.refund_data?.raw?.data?.metadata
          ?.clientReferenceInformation?.code ||
        "N/A",
      reconciliationId:
        result?.data?.refund_data?.raw?.data?.metadata?.reconciliationId ||
        "N/A",
      networkTransactionId:
        result?.data?.refund_data?.raw?.data?.metadata?.processorInformation
          ?.networkTransactionId || "N/A",
    };
  }

  console.log("prepareRefundData - Final data:", refundData);
  return refundData;
}
