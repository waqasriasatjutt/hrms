import { CustomerDisplay } from "@point_of_sale/customer_display/customer_display";
import { CustomerDisplayQRPopup } from "@pos_qr30_scb/app/utils/customer_display_qr_popup/customer_display_qr_popup";

import { patch } from "@web/core/utils/patch";

patch(CustomerDisplay.prototype, {
  showQR() {
    if (this.order.qr30ShowOnCustomerDisplay) {
      this.dialog.add(CustomerDisplayQRPopup, {
        qrCode: this.order.qr30Data.qrImage,
        shopName: this.order.qr30Data.shopName,
        amount: this.order.qr30Data.formattedAmount,
        expireTime: this.order.qr30Data.expireTime,
      });
    }
  },
  hidePopup() {
    this.dialog.closeAll();
  },
});
