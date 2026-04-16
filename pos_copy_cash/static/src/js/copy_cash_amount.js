/** @odoo-module **/

import { ClosePosPopup } from "@point_of_sale/app/navbar/closing_popup/closing_popup";
import { patch } from "@web/core/utils/patch";

console.log("pos_copy_cash: module loaded (minimal)");

const _orig_setup = ClosePosPopup.prototype.setup;

patch(ClosePosPopup.prototype, {
  setup() {
    const res = _orig_setup?.apply(this, arguments);
    const cmp = this;

    const insert = () => {
      const popup = document.querySelector(".popup.close-pos-popup");
      if (!popup) return false;
      const money =
        popup.querySelector("td.d-flex div.button.ClosePosPopup") ||
        popup.querySelector('i[title="Open the money details popup"]')?.closest("div.button");
      if (!money || money.parentNode.querySelector(".o_pos_copy_btn")) return !!money;
      const btn = document.createElement("div");
      btn.className = "button icon ClosePosPopup btn o_pos_copy_btn";
      btn.innerHTML = '<i class="fa fa-copy fa-2x"></i>';
      btn.title = "Copy expected → counted";
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        cmp.copyAction?.();
      });
      money.parentNode.insertBefore(btn, money.nextSibling);
      console.log("pos_copy_cash: button inserted");
      return true;
    };

    if (!insert()) {
      let tries = 0, id = setInterval(() => { if (insert() || ++tries > 8) clearInterval(id); }, 150);
    }
    return res;
  },

  copyAction() {
    const cash = this.props?.default_cash_details;
    if (!cash) return console.warn("pos_copy_cash: no default cash");
    const expected = cash.amount ?? 0;
    const formatted = this.env.utils.formatCurrency(expected, false);
    this.state.payments = this.state.payments || {};
    this.state.payments[cash.id] = this.state.payments[cash.id] || { counted: "" };
    this.state.payments[cash.id].counted = formatted;
    console.log("pos_copy_cash: copied expected → counted", expected);
  },
});
