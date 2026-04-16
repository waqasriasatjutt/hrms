import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

patch(PosOrder.prototype, {
  showQRcodeOnCustomerDisplay() {
    this.qr30ShowOnCustomerDisplay = true;
  },
  hideQRcodeOnCustomerDisplay() {
    this.qr30ShowOnCustomerDisplay = false;
  },

  getCustomerDisplayData() {
    const data = super.getCustomerDisplayData();

    data.qr30ShowOnCustomerDisplay = this.qr30ShowOnCustomerDisplay || false;
    data.qr30Data = {
      qrImage: this.qr30Payment?.qr30_image,
      shopName: this.qr30Payment?.payment_method_id.qr30_biller_name,
      formattedAmount: this.qr30FormattedAmount,
      expireTime: this.qr30Payment?.qr30_expire_time
        ? this.qr30Payment.qr30_expire_time.toJSDate()
        : undefined,
    };

    return data;
  },

  setQR30PaymentLine(payment) {
    this.qr30Payment = payment;
  },
  getQR30PaymentLine() {
    return this.qr30Payment;
  },
  clearQR30PaymentLine() {
    this.qr30Payment = undefined;
  },
  hasQR30PaymentLine() {
    return this.qr30Payment !== undefined;
  },

  setQR30PaymentFeeProductId(productId) {
    this.qr30PaymentFeeProductId = productId;
  },
  getQR30PaymentFeeProductId() {
    return this.qr30PaymentFeeProductId;
  },

  setQR30FormattedAmount(str) {
    this.qr30FormattedAmount = str;
  },
});
