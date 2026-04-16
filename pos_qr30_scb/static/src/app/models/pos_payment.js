import { PosPayment } from "@point_of_sale/app/models/pos_payment";
import { patch } from "@web/core/utils/patch";

const { DateTime } = luxon;

patch(PosPayment.prototype, {
  handle_payment_response(isPaymentSuccessful) {
    if (this.payment_method_id.qr_code_method != "qr30")
      return super.handle_payment_response(isPaymentSuccessful);

    if (this.get_payment_status() === "done") return true;

    if (isPaymentSuccessful) {
      // this.set_payment_status("qr30ForceDone");
      this.set_payment_status("done");
      return true;
    } else if (
      this.qr30_expire_time &&
      this.qr30_expire_time <= DateTime.now()
    ) {
      this.set_payment_status("expired");
    }

    return isPaymentSuccessful;
  },

  setQRdata(data) {
    if (data == undefined) return;

    this.qr30_ref1 = data.ref1;
    this.qr30_ref2 = data.ref2;
    this.qr30_ref3 = data.ref3;
    this.qr30_raw_data = data.qrRawData;
    this.qr30_image = data.qrImage;
    this.qr30_expire_time = DateTime.now().plus({
      seconds: this.payment_method_id.qr30_payment_timer,
    });

    this.set_payment_status("waitingPayment");
  },

  setTransactionDetails(data) {
    if (data == undefined) return;

    this.qr30_transaction_type = data.transactionType;
    // this.qr30_transaction_time = data.transactionDateandTime
    //   ? DateTime.fromISO(data.transactionDateandTime, { zone: "utc" })
    //   : undefined;
    this.qr30_payer_bank = data.sendingBankCode;
    this.qr30_payer_account_name = data.payerName;
    this.qr30_payer_account_number = data.payerAccountNumber;

    this.set_payment_status("done");
  },
});
