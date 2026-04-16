import {
    BACKSPACE,
    DEFAULT_LAST_ROW,
} from "@point_of_sale/app/generic_components/numpad/numpad";
import {TicketScreen} from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import {_t} from "@web/core/l10n/translation";
import {getCustomButtons} from "./numpad";
import {patch} from "@web/core/utils/patch";

patch(TicketScreen.prototype, {
    // Override the method for call the new custom method. #T8410
    getNumpadButtons() {
        return getCustomButtons(DEFAULT_LAST_ROW, [
            {value: "quantity", text: _t("Qty"), class: "active border-primary"},
            {value: "discount", text: _t("% Disc"), disabled: true},
            {value: "price", text: _t("Price"), disabled: true},
            BACKSPACE,
        ]);
    },
});
