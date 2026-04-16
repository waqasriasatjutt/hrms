/** @odoo-module **/
import { _t } from "@web/core/l10n/translation";
import { Component, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";

export class LealPointsChoicePopup extends Component {
    static template = "Plugin_Leal.LealPointsChoicePopup";
    static components = { Dialog };
    setup() {
        super.setup();
        this.state = useState({
            montoRedimir: this.props.valorPesos,
        });
    }

    onInputChange(ev) {
        this.state.montoRedimir = parseInt(ev.target.value) || 0;
    }

    confirmAll() {
        this.props.getPayload({ confirmed: true, useAll: true, monto: this.props.valorPesos });
        this.props.close();
    }

    confirmMonto() {
        this.props.getPayload({ confirmed: true, useAll: false, monto: this.state.montoRedimir });
        this.props.close();
    }

    cancel() {
        this.props.getPayload({ confirmed: false });
        this.props.close();
    }
}
