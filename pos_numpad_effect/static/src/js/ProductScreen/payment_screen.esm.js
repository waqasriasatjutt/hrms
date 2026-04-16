import {ProductScreen} from "@point_of_sale/app/screens/product_screen/product_screen";
import {patch} from "@web/core/utils/patch";
import {useRef} from "@odoo/owl";

patch(ProductScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this.numpadWidgetBlinkEffect = useRef("NumpadWidgetBlinkEffect");
    },

    // Inherit the method for set the timeout effect of number. #T8409
    onNumpadClick(buttonValue) {
        super.onNumpadClick(buttonValue);
        if (
            buttonValue !== "Backspace" &&
            buttonValue !== "-" &&
            buttonValue !== "." &&
            buttonValue !== "quantity" &&
            buttonValue !== "discount" &&
            buttonValue !== "price"
        ) {
            const tmp = document.createElement("span");
            tmp.textContent = buttonValue;
            this.numpadWidgetBlinkEffect.el.append(tmp);
            setTimeout(() => this.numpadWidgetBlinkEffect.el.removeChild(tmp), 175);
        }
    },
});
