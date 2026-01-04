import { patch } from "@web/core/utils/patch";
import { NumberPopup } from "@point_of_sale/app/utils/input_popups/number_popup";

patch(NumberPopup.prototype, {
    setup() {
        super.setup(...arguments);
        const title = (this.props?.title || "").toLowerCase();
        // Set a flag on the numberBuffer service to skip formatting
        this.numberBuffer.isPinEntry =
            title.includes("password") ||
            title.includes("passcode") ||
            title.includes("pin");
    },

confirm() {
    // PIN popup → RAW value
    if (this.numberBuffer.isPinEntry) {
        this.props.getPayload(String(this.state.buffer ?? ""));
        this.props.close();
        return;
    }

    // Normal popups (discount, qty, price, etc.)
    let buffer = this.state.buffer;

    // ✅ Normalize buffer
    if (buffer === undefined || buffer === null) {
        buffer = "";
    } else if (typeof buffer !== "string") {
        buffer = String(buffer);
    }

    buffer = buffer.replace(/,/g, "");

    this.props.getPayload(buffer);
    this.props.close();
},
});
