/** @odoo-module **/

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

import {
    BACKSPACE,
    ZERO,
    DECIMAL,
    DEFAULT_LAST_ROW,
    getButtons,
} from "@point_of_sale/app/generic_components/numpad/numpad";

patch(ProductScreen.prototype, {
    setup() {
        super.setup();
        // Initialize discount mode: "percent" or "amount"
        if (!this.pos.discountMode) {
            this.pos.discountMode = "amount";
        }
        this._discountLastClick = 0; // for double click detection
    },

    getNumpadButtons() {
        const decimalPoint = this.env.services.localization.decimalPoint;
        const colorClassMap = {
            [decimalPoint]: "o_colorlist_item_color_transparent_6",
            Backspace: "o_colorlist_item_color_transparent_1",
            "-": "o_colorlist_item_color_transparent_3",
        };

        const discountButton =
            this.pos.discountMode === "percent"
                ? { value: "discount", text: _t("Disc %"), disabled: !this.pos.config.manual_discount }
                : { value: "discount_number", text: _t("Disc Amt"), disabled: !this.pos.config.manual_discount };

        return getButtons(DEFAULT_LAST_ROW, [
            { value: "quantity", text: _t("Qty") },
            discountButton,
            {
                value: "price",
                text: _t("Price"),
                disabled: !this.pos.cashierHasPriceControlRights(),
            },
            BACKSPACE,
        ]).map((button) => ({
            ...button,
            class: `
                ${colorClassMap[button.value] || ""}
                ${this.pos.numpadMode === button.value ? "active" : ""}
                ${button.value === "quantity" ? "numpad-qty rounded-0 rounded-top mb-0" : ""}
                ${button.value === "price" ? "numpad-price rounded-0 rounded-bottom mt-0" : ""}
                ${
                    ["discount", "discount_number"].includes(button.value)
                        ? "numpad-discount my-0 rounded-0 border-top border-bottom"
                        : ""
                }
            `,
        }));
        // 🧠 Add restriction for Backspace dynamically
        const cashier = this.pos.get_cashier?.();
        // if (cashier && cashier._is_restrict_remove_line) {
        //     buttons.forEach((b) => {
        //         if (b.value === "Backspace") {
        //             b.disabled = true;
        //         }
        //     });
        // }

        return buttons;
    },

    // onNumpadClick(buttonValue) {
    //     if (["quantity", "discount", "price", "discount_number"].includes(buttonValue)) {
    //         this.numberBuffer.capture();
    //         this.numberBuffer.reset();
    //         this.pos.numpadMode = buttonValue;
    //         return;
    //     }
    //     this.numberBuffer.sendKey(buttonValue);
    // },
    onNumpadClick(buttonValue) {
        const line = this.currentOrder?.get_selected_orderline?.();
        const cashier = this.pos.get_cashier?.();
        const qty = line ? Number(line.get_quantity?.() || line.quantity || 0) : 0;

        // Handle Backspace restriction
        if (line && buttonValue === "Backspace" && qty <= 1 && cashier?._is_restrict_remove_line) {
            this.env.services.notification.add("You are not allowed to remove this order line.", { type: "warning" });
            return;
        }

        // Restrict reducing quantity below 1 using number buffer
        if (buttonValue === "-" && line && qty <= 1 && cashier?._is_restrict_remove_line) {
            this.env.services.notification.add("You cannot reduce quantity below 1 for this order line.", { type: "warning" });
            return;
        }

        // Handle mode buttons
if (["quantity", "discount", "price", "discount_number"].includes(buttonValue)) {
    this.numberBuffer.capture();
    this.numberBuffer.reset();

    // 🔁 Handle discount toggle on double click / long press simulation
    if (buttonValue === "discount" || buttonValue === "discount_number") {
        const now = new Date().getTime();
        if (now - this._discountLastClick < 500) { // double click threshold
            // toggle discount mode
            this.pos.discountMode = this.pos.discountMode === "percent" ? "amount" : "percent";

            // sync the active button to new mode
            this.pos.numpadMode = this.pos.discountMode === "percent" ? "discount" : "discount_number";

            this._discountLastClick = 0;
        } else {
            this._discountLastClick = now;

            // set mode normally for first click
            this.pos.numpadMode = buttonValue;
        }
    } else {
        this.pos.numpadMode = buttonValue;
    }

    return;
}

        // Default: send key to numberBuffer
        this.numberBuffer.sendKey(buttonValue);
    },

    onKeyDown(ev) {
        const line = this.currentOrder?.get_selected_orderline?.();
        const cashier = this.pos.get_cashier?.();
        const qty = line ? Number(line.get_quantity?.() || line.quantity || 0) : 0;
        const restrictedKeys = ["Backspace", "Delete", "Minus", "-"];

        if (line && qty <= 1 && cashier?._is_restrict_remove_line && restrictedKeys.includes(ev.key)) {
            this.env.services.notification.add("You are not allowed to remove or reduce this order line.", { type: "warning" });
            ev.preventDefault();
            ev.stopPropagation();
            return;
        }

        super.onKeyDown(ev);
    },
});