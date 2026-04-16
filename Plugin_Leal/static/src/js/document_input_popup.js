/** @odoo-module **/

import { AbstractAwaitablePopup } from "@point_of_sale/app/utils/abstract_awaitable_popup";;
import { useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";

export class DocumentInputPopup extends AbstractAwaitablePopup {
    static template = "DocumentInputPopup";
    static defaultProps = {
        confirmText: _t("Buscar"),
        cancelText: _t("Cancelar"),
        title: _t("Número de Documento"),
        body: _t("Ingrese el número de documento del cliente:"),
    };

    setup() {
        super.setup();
        this.state = useState({
            inputValue: "",
        });
    }

    getPayload() {
        return {
            inputValue: this.state.inputValue.trim(),
        };
    }

    onInputChange(event) {
        this.state.inputValue = event.target.value;
    }

    onInputKeydown(event) {
        if (event.key === "Enter") {
            this.confirm();
        }
    }
    close() {
        super.close();
        this.state.inputValue = "";
    }
}
