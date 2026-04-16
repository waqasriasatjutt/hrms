/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Message } from "@mail/core/common/message_model";
import { browser } from "@web/core/browser/browser";
import { _t } from "@web/core/l10n/translation";

// Patch the Message model to handle payment links
patch(Message.prototype, {
  /**
   * Override the copyLink method to handle payment links specially
   */
  async copyLink() {
    // Check if this message contains a payment link
    if (this.body && this.body.includes("Payment link created")) {
      // Try to find the link in the body (including hidden spans)
      const linkMatch = this.body.match(
        /https:\/\/ebctest\.cybersource\.com[^"'\s<>]+/
      );
      if (linkMatch) {
        const paymentLink = linkMatch[0];
        let notification = _t("Payment Link Copied!");
        let type = "info";
        try {
          await browser.navigator.clipboard.writeText(paymentLink);
        } catch {
          notification = _t("Payment Link Copy Failed (Permission denied?)!");
          type = "danger";
        }
        this.store.env.services.notification.add(notification, { type });
        return;
      }
    }

    // Fallback to original behavior for non-payment links
    return super.copyLink();
  },
});
