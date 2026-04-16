/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosOrder } from "@point_of_sale/app/models/pos_order";

//Config here the fields, order and label that you want to show
const PAYRILLIUM_RECEIPT_FIELDS = [
  { key: "transactionId", label: "Transaction ID" },
  { key: "cardType", label: "Card Type" },
  { key: "cardNumber", label: "Card Number" },
  { key: "entryMode", label: "Entry Mode" },
  { key: "TVR", label: "TVR (Terminal Verification Results)" },
  { key: "AID", label: "AID (Application Identifier)" },
  { key: "ATC", label: "ATC (Application Transaction Counter)" },
  // same for APPPN and APPLAB
  { key: "ApplicationLabel", label: "APPLAB (Application Label)" },
  {
    key: "ApplicationLabel",
    label: "APPPN (Application Preferred Name)",
  },
  { key: "CVM", label: "CVM (Cardholder Verification Method)" },
  { key: "approvalCode", label: "Approval Code" },
  { key: "cardVendor", label: "Card Vendor" },
  { key: "date", label: "Date" },
  { key: "status", label: "Status" },
  { key: "responseCodeMeaning", label: "Status Code" },
  { key: "responseCode", label: "Response Code" },

  { key: "ApplicationCryptogram", label: "TC" },
];

patch(PosOrder.prototype, {
  export_for_printing() {
    const data = super.export_for_printing(...arguments);

    const payrilliumInfo = this.get_extra_payment_data?.() || {};
    const payrilliumInfoList = PAYRILLIUM_RECEIPT_FIELDS.filter(
      (f) =>
        payrilliumInfo[f.key] !== undefined && `${payrilliumInfo[f.key]}` !== ""
    ).map((f) => ({ label: f.label, value: payrilliumInfo[f.key] }));

    return { ...data, payrilliumInfo, payrilliumInfoList };
  },

  set_extra_payment_data(data) {
    this.extra_payment_data = data;
  },
  get_extra_payment_data() {
    return this.extra_payment_data || {};
  },
});

/*
 * Payrillium/EMV Receipt Displayable Variables
 * --------------------------------------------
 * The following variables can be displayed on the POS receipt.
 * These are extracted from the Payrillium response and EMV tags (emvTags).
 * To control which fields are shown and their order, configure the PAYRILLIUM_RECEIPT_FIELDS array.
 *
 * Available keys (examples included):
 *
 * cardType                // e.g. "DEBIT"
 * approvalCode            // e.g. "831000"
 * cardVendor              // e.g. "VISA"
 * cardNumber              // e.g. "5228"
 * transactionId           // e.g. "1747242219370"
 * terminalId              // e.g. "87654321"
 * entryMode               // e.g. "CONTACTLESS"
 * date                    // e.g. "2025-05-15T01:03:39Z"
 * status                  // e.g. "AUTHORIZED"
 * TVR                     // Terminal Verification Results, e.g. "0000000000"
 * FormFactorIndicator     // e.g. "23880000"
 * AID                     // Application Identifier, e.g. "A0000000031010"
 * PANSequence             // e.g. "00"
 * DFName                  // e.g. "A0000000031010"
 * ApplicationCryptogram   // e.g. "60C9B64607C171D3"
 * IssuerAppData           // e.g. "1F420132A0000000001003027300000000400000000000000000000000000000"
 * ATC                     // Application Transaction Counter, e.g. "0193"
 * APPLAB                  // Application Label, e.g. "VISA DEBIT"
 * APPPN                   // Application Preferred Name, e.g. "VISA DEBIT"
 * AIP                     // e.g. "0060"
 * TransactionDate         // e.g. "250515"
 * TransactionType         // e.g. "00"
 * CurrencyCode            // e.g. "0840"
 * AmountAuthorized        // e.g. "000000000283"
 * AmountOther             // e.g. "000000000000"
 * TerminalCountryCode     // e.g. "0840"
 * CryptogramInfo          // e.g. "80"
 * UnpredictableNumber     // e.g. "5146D27C"
 *
 * Use these keys in PAYRILLIUM_RECEIPT_FIELDS to control which fields are shown and their order.
 */
