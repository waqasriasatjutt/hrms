/** @odoo-module **/

import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { payrilliumBus } from "./utils";
import { rpc as rpcRequest } from "@web/core/network/rpc";

patch(Navbar.prototype, {
  setup() {
    super.setup();
    this.orm = useService("orm");
    this.notification = useService("notification");

    if (!this.pos.terminalStatus) {
      this.pos.terminalStatus = "unknown";
    }

    payrilliumBus.addEventListener("payrillium:terminal_offline", () => {
      console.log("Terminal went offline");
      this.pos.terminalStatus = "offline";
      this.render();
    });

    this.checkTerminalStatus();
  },

  get terminalStatusText() {
    return this.pos.terminalStatus === "online"
      ? "🟢 Terminal Online"
      : "🔴 Terminal Offline";
  },

  get terminalCssClass() {
    return this.pos.terminalStatus === "online" ? "success" : "danger";
  },

  get terminalIsVisible() {
    // Early return if pos is not ready or no terminal configured
    if (
      !this.pos ||
      !this.pos.config ||
      !this.pos.config.payrillium_terminal_serial
    ) {
      return false;
    }

    // Early return if mainScreen is not ready
    if (!this.pos.mainScreen || !this.pos.mainScreen.component) {
      return false;
    }

    const component = this.pos.mainScreen.component;
    const currentScreen =
      component.constructor?.name || component.name || "OtherScreen";

    return currentScreen === "ProductScreen";
  },

  async checkTerminalStatus() {
    try {
      const serial = this.pos.config.payrillium_terminal_serial;
      console.log(serial, "serial");

      if (!serial) {
        this.pos.terminalStatus = "offline";
        this.notification.add("  No terminal assigned to this POS config.", {
          type: "danger",
        });
        return;
      }

      const result = await rpcRequest("/payrillium/check_terminal_backend", {
        terminal_id: serial,
      });

      console.log(result, "result");

      if (
        result?.status === "success" &&
        result?.data?.data?.success === true
      ) {
        this.pos.terminalStatus = "online";
        this.notification.add("  Terminal is online", { type: "success" });
      } else {
        console.log("Terminal check result:", result);
        this.pos.terminalStatus = "offline";
        const msg = result?.message || "Unknown error";
        this.notification.add("   Terminal offline: " + msg, {
          type: "danger",
        });
      }
    } catch (error) {
      this.pos.terminalStatus = "offline";
      this.notification.add("  Failed to contact terminal", {
        type: "danger",
      });
      console.error("Terminal status check failed:", error);
    }
  },
});
