/** @odoo-module **/
import { EventBus } from "@odoo/owl";

const payrilliumBus = new EventBus();

export { payrilliumBus };

export function parseEMVData(
  emvTagsHex,
  options = { flatten: true, simpleDecode: true }
) {
  const knownTags = {
    "4F": "AID",
    50: "ApplicationLabel",
    "5F34": "PANSequence",
    "5F2A": "CurrencyCode",
    82: "AIP",
    84: "DFName",
    "9A": "TransactionDate",
    "9C": "TransactionType",
    "9F02": "AmountAuthorized",
    "9F03": "AmountOther",
    "9F06": "AIDAlt",
    "9F10": "IssuerAppData",
    "9F12": "ApplicationPreferredName",
    "9F1A": "TerminalCountryCode",
    "9F26": "ApplicationCryptogram",
    "9F27": "CryptogramInfo",
    "9F34": "CVM",
    "9F36": "ATC",
    "9F37": "UnpredictableNumber",
    "9F6E": "FormFactorIndicator",
    95: "TVR",
    70: "ResponseTemplate1",
    77: "ResponseTemplate2",
    "6F": "FCITemplate",
    A5: "FCIProprietary",
    61: "ApplicationTemplate",
    BF0C: "FCIIssuerDiscretionary",
  };
  function hexToBytes(h) {
    const out = [];
    for (let i = 0; i < h.length; i += 2)
      out.push(parseInt(h.substr(i, 2), 16));
    return Uint8Array.from(out);
  }
  function bytesToAscii(bytes) {
    return Array.from(bytes)
      .map((b) => String.fromCharCode(b))
      .join("");
  }
  function isConstructed(firstByte) {
    return (firstByte & 0x20) === 0x20; // bit 6
  }
  function readTag(s, i) {
    const b1 = parseInt(s.substr(i, 2), 16);
    let tag = s.substr(i, 2);
    i += 2;
    if ((b1 & 0x1f) === 0x1f) {
      // keep reading while MSB=1
      while (i + 2 <= s.length) {
        const b = parseInt(s.substr(i, 2), 16);
        tag += s.substr(i, 2);
        i += 2;
        if ((b & 0x80) === 0) break;
      }
    }
    return { tag: tag.toUpperCase(), next: i, firstByte: b1 };
  }
  function readLength(s, i) {
    const first = parseInt(s.substr(i, 2), 16);
    i += 2;
    if ((first & 0x80) === 0) {
      return { len: first, next: i }; // short form
    }
    const nBytes = first & 0x7f;
    let len = 0;
    for (let k = 0; k < nBytes; k++) {
      len = (len << 8) | parseInt(s.substr(i, 2), 16);
      i += 2;
    }
    return { len, next: i };
  }

  function decodeValue(tag, valueHex) {
    const bytes = hexToBytes(valueHex);
    if (options.simpleDecode) {
      const ascii = bytesToAscii(bytes);
      const printable = /^[\x20-\x7E]*$/.test(ascii);
      return printable ? ascii : valueHex;
    }
    // richer decoding examples (toggle simpleDecode=false to use)
    const t = tag.toUpperCase();
    if (t === "50" || t === "9F12" || t === "84") {
      const ascii = bytesToAscii(bytes);
      return /^[\x20-\x7E]*$/.test(ascii) ? ascii : valueHex;
    }
    if (t === "9A") {
      const yy = valueHex.slice(0, 2),
        mm = valueHex.slice(2, 4),
        dd = valueHex.slice(4, 6);
      return `20${yy}-${mm}-${dd}`;
    }
    if (t === "5F2A" || t === "9F1A") return parseInt(valueHex, 16);
    // default: keep hex
    return valueHex;
  }

  function parseTLV(s, start = 0, end = s.length) {
    const out = {};
    let i = start;
    while (i < end) {
      if (i + 2 > s.length) break;
      const { tag, next: iTag, firstByte } = readTag(s, i);
      i = iTag;

      if (i + 2 > s.length) break;
      const { len, next: iLen } = readLength(s, i);
      i = iLen;

      const vEnd = i + len * 2;
      if (vEnd > s.length) break; // safety

      const valueHex = s.substring(i, vEnd);
      i = vEnd;

      if (isConstructed(firstByte)) {
        out[tag] = parseTLV(valueHex, 0, valueHex.length);
      } else {
        out[tag] = decodeValue(tag, valueHex);
      }
    }
    return out;
  }

  const list = parseTLV(emvTagsHex);

  function flatten(obj, acc = {}) {
    for (const [k, v] of Object.entries(obj)) {
      if (v && typeof v === "object" && !Array.isArray(v)) {
        flatten(v, acc);
      } else {
        acc[k] = v;
      }
    }
    return acc;
  }

  const byTag = options.flatten ? flatten(list) : list;
  const result = {};
  for (const [t, v] of Object.entries(byTag)) {
    result[knownTags[t] || t] = v; // keep your friendly names
  }
  return result;
}

export const ARC_MEANING = {
  "00": "Approved",
  "01": "Referral",
  "05": "Do not honor / Declined",
  51: "Insufficient funds",
  54: "Expired card",
  91: "Issuer or switch inoperative",
  96: "System malfunction",
};
export function mapCVMCode(code) {
  const cvmMethods = {
    0: "Fail CVM processing",
    1: "Offline plaintext PIN",
    2: "Online enciphered PIN",
    3: "Offline plaintext PIN + signature (paper)",
    4: "Offline enciphered PIN",
    5: "Offline enciphered PIN + signature (paper)",
    8: "Enciphered PIN verified online",
    30: "Signature (paper)",
    31: "No CVM required",
  };
  const numericCode = parseInt(code, 10);
  return cvmMethods[numericCode] || "NONE";
}
export function generateExecutionId() {
  return Math.random().toString(36).substring(2, 10) + Date.now();
}

/**
 * Check if the payment was cancelled by the user.
 * Examples: message === "ABORTED" or state === "CANCELLED"
 */
export function isCancelled(result) {
  const state = result?.data?.state;
  const message = result?.data?.data?.message;
  return state === "CANCELLED" || message === "ABORTED";
}

/**
 * Check if the payment failed (not cancelled, but unsuccessful).
 * We consider any result with success === false as a failure,
 * except if it was cancelled.
 */
export function isFailed(result) {
  const success = result?.data?.success;
  const status = result?.data?.data?.message?.status || result?.data?.status;
  const isDeclined = status?.toUpperCase?.() === "DECLINED";
  return (success === false || isDeclined) && !isCancelled(result);
}

/**
 * Get a user-friendly message based on the result.
 */
export function getPayrilliumMessage(result) {
  if (isCancelled(result)) {
    return "Operation cancelled by user.";
  }
  if (isFailed(result)) {
    return "There was a problem with this card. Please try another one.";
  }
  return "Payment processed successfully.";
}

/**
 * Validate the result and throw an error if it failed or was cancelled.
 * If allowCancelled is true, cancelled operations won't throw.
 */
export function validatePayrilliumResponse(
  result,
  { allowCancelled = false } = {}
) {
  if (
    (result?.status === "error" || result?.success == false) &&
    typeof result?.message === "string"
  ) {
    const msg = result.message.toUpperCase();
    if (
      msg.includes("409 CLIENT ERROR") ||
      msg.includes("500 SERVER ERROR") ||
      msg.includes("404 CLIENT ERROR")
    ) {
      console.log("terminal_offline");

      payrilliumBus.trigger("payrillium:terminal_offline");
      const error = new Error(
        "Before proceeding, please verify the connection with the terminal."
      );
      error.payrilliumError = true;
      error.terminalConnectionError = true;
      throw error;
    }

    const error = new Error(result.message);
    error.payrilliumError = true;
    throw error;
  }
  if (isCancelled(result)) {
    if (allowCancelled) {
      return { cancelled: true, message: "Operation cancelled by user." };
    }
    const error = new Error("Operation cancelled by user.");
    error.payrilliumError = true;
    error.cancelled = true;
    throw error;
  }

  if (isFailed(result)) {
    const error = new Error(
      "There was a problem with this card. Please try another one."
    );
    error.payrilliumError = true;
    throw error;
  }

  return { success: true };
}

export function updateTransactionState(step, response) {
  const status = response?.data?.data?.message?.status?.toUpperCase() || "";

  switch (status) {
    case "DECLINED":
    case "FAILED":
    case "REJECTED":
    case "SYSTEM_ERROR":
    case "PAX_ERROR":
      return "error";
    case "CANCELLED":
      return "cancel";
    case "PENDING":
      return "done";
    case "APPROVED":
    case "SUCCESS":
    case "SUCCESS_AUTH":
    case "AUTHORIZED":
      return step === "authorize" ? "authorized" : "done";
    default:
      return "draft";
  }
}
export async function logPayrilliumError(
  rpc,
  {
    executionId = "missing",
    step = "unspecified_step",
    kind = "response",
    success = false,
    errorMessage = "",
    payload = {},
  }
) {
  console.log(
    "    logPayrilliumError",
    executionId,
    step,
    kind,
    success,
    errorMessage,
    payload
  );
  console.log(rpc, "rpc");

  try {
    await rpc("/payrillium/log", {
      execution_id: executionId,
      step,
      kind,
      success,
      error_message: errorMessage,
      payload,
    });
  } catch (e) {
    console.warn("   Failed to log Payrillium error from JS", e);
  }
}

/**
 * Map card vendor codes to their corresponding names.
 * @type {Object}
 * @property {string} "001" - VISA
 * @property {string} "002" - MASTERCARD
 * @property {string} "003" - AMERICAN EXPRESS
 * @property {string} "004" - DISCOVER
 * @property {string} "005" - DINERS CLUB
 * @property {string} "006" - CARTE BLANCHE
 * @property {string} "007" - JCB
 * @property {string} "033" - VISA ELECTRON
 */
export const CARD_VENDOR = {
  "001": "VISA",
  "002": "MASTERCARD",
  "003": "AMERICAN EXPRESS",
  "004": "DISCOVER",
  "005": "DINERS CLUB",
  "006": "CARTE BLANCHE",
  "007": "JCB",
  "033": "VISA ELECTRON",
};
