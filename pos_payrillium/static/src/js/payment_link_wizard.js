/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { CopyButton } from "@web/core/copy_button/copy_button";
import { rpc as rpcRequest } from "@web/core/network/rpc";

// In-memory cache to avoid duplicate link generation during session
const generatedLinksCache = new Map();

patch(CopyButton.prototype, {
  setup() {
    super.setup();
    this.orm = useService("orm");
    this.notification = useService("notification");
  },

  async onClick() {
    console.log(this.props, "this.props");

    console.log("  Starting onClick", {
      content: this.props.content,
      className: this.props.className,
    });

    // Check if this is a standard Odoo payment link (not Payrillium)
    const isPaymentLink = this.props.content?.includes("/payment/pay");
    if (!isPaymentLink) {
      // This is not a standard Odoo payment link (might be Payrillium link already)
      // Just use the default behavior (copy as-is)
      return super.onClick();
    }

    // Check if Payrillium is configured before intercepting
    try {
      const configCheck = await rpcRequest("/payrillium/check_config", {});
      if (!configCheck || !configCheck.configured) {
        // Payrillium not configured, use standard Odoo behavior
        console.log("  Payrillium not configured, using standard Odoo link");
        return super.onClick();
      }
    } catch (error) {
      // If config check fails, fallback to standard behavior
      console.error("  Error checking Payrillium config:", error);
      return super.onClick();
    }

    try {
      const url = new URL(this.props.content);

      const amount = url.searchParams.get("amount");
      const invoiceId =
        url.searchParams.get("move_id") || url.searchParams.get("invoice_id");

      if (!amount || !invoiceId) {
        // Missing required params, use standard behavior
        return super.onClick();
      }

      const cacheKey = `${invoiceId}_${amount}`;
      if (generatedLinksCache.has(cacheKey)) {
        const cachedLink = generatedLinksCache.get(cacheKey);
        console.log(" Using cached link:", cachedLink);
        await navigator.clipboard.writeText(cachedLink);
        this.notification.add("Payment link copied (cached)", { type: "info" });
        return;
      }

      const resp = await rpcRequest("/payrillium/generate_link", {
        model: "account.move",
        id: invoiceId,
        amount: parseFloat(amount),
      });

      if (!resp) {
        this.notification.add("Failed to generate link: empty response", {
          type: "danger",
        });
        return;
      }

      if (resp.success !== true) {
        const msg =
          resp.error || "Failed to generate payment link (server side)";
        this.notification.add(msg, { type: "danger" });
        return;
      }

      const newLink = resp.link;
      if (!newLink) {
        this.notification.add("Server reported success but returned no link", {
          type: "danger",
        });
        return;
      }

      generatedLinksCache.set(cacheKey, newLink);
      await navigator.clipboard.writeText(newLink);

      // Show warning if it's an existing link, otherwise show success
      if (resp.warning) {
        this.notification.add(resp.warning, { type: "warning" });
      } else {
        this.notification.add("Payment link copied", { type: "success" });
      }
    } catch (error) {
      console.error("  Error:", error);
      this.notification.add("Failed to generate/copy link", { type: "danger" });
    }
  },
});

console.log("  CopyButton patch with session cache ready");
