/** @odoo-module **/

//import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { useState, Component } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";

export class PromotionCodePopup extends Component {
    static template = "Plugin_Leal.PromotionCodePopup";
    static components = { Dialog };
    static defaultProps = {
        title: _t("Código de Promoción"),
        body: _t("Ingrese los últimos dígitos del código de promoción"),
    };

    setup() {
        super.setup();
        this.orm = useService("orm");
        this.state = useState({
            promotionCode: "",
            isValid: false,
            hiddenCharacters: this.props.hiddenCharacters || 4,
        });
    }

    cancel() {
        this.props.close({
            promotionCode: null,
            confirmed: false,
        });
    }

    confirm() {
        this.props.getPayload({
            promotionCode: this.state.promotionCode, confirmed: true
        });
        this.props.close();
    }

    onInputChange(event) {
        const value = event.target.value.slice(0, this.state.hiddenCharacters);
        this.state.promotionCode = value;
        this.state.isValid = this.state.promotionCode.trim().length === this.state.hiddenCharacters;
    }

    maskPromotionCode(code) {
        if (!code || code.length <= this.state.hiddenCharacters) {
            return code;
        }
        const visiblePart = code.slice(0, -this.state.hiddenCharacters);
        const maskedPart = 'X'.repeat(this.state.hiddenCharacters);
        return visiblePart + maskedPart;
    }

    get maskedCode() {
        return this.maskPromotionCode(this.props.promotionCode);
    }
}