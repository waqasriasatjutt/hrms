/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { LoadingIndicator } from "@web/webclient/loading_indicator/loading_indicator";

patch(LoadingIndicator.prototype, {
  setup() {
    super.setup();
    this._loaderTimer = null;
    this._overlayVisible = false;

    this.env.bus.addEventListener("RPC:REQUEST", () => {
      if (!this._loaderTimer) {
        this._loaderTimer = setTimeout(() => {
          this._showOverlay();
          this._loaderTimer = null;
        }, 500);
      }
    });

    this.env.bus.addEventListener("RPC:RESPONSE", () => {
      if (this._loaderTimer) {
        clearTimeout(this._loaderTimer);
        this._loaderTimer = null;
      }
      this._hideOverlay();
    });
  },

  _showOverlay() {
    if (this._overlayVisible) return;
    const existing = document.getElementById("fullscreen_loader_overlay");
    if (!existing) {
      const loader = document.createElement("div");
      loader.id = "fullscreen_loader_overlay";
      loader.className = "fullscreen-loader";
      loader.innerHTML = `
        <div class="spinner"></div>
        <div class="loading-text">Please wait...</div>
      `;
      document.body.appendChild(loader);
    }
    this._overlayVisible = true;
  },

  _hideOverlay() {
    const existing = document.getElementById("fullscreen_loader_overlay");
    if (existing) {
      existing.remove();
    }
    this._overlayVisible = false;
  },
});
