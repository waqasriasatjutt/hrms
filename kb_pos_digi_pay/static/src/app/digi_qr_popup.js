/** @odoo-module **/

import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { Dialog } from "@web/core/dialog/dialog";

export class DigiPayQrPopup extends Component {
    static template = "kb_pos_digi_pay.DigiPayQrPopup";
    static components = { Dialog };
    static props = ["*"];

    setup() {
        this.dialog = useService("dialog");
        this.env.dialogData.dismiss = () => this._dismiss();
    }

    _dismiss() {
        this.props.onDismiss();
        this.props.close();
    }

    get qrData() {
        return this.props.qrCode || "";
    }

    get amount() {
        return this.props.amount || 0;
    }

    onCancel() {
        // Эхлээд onCancel prop-ийг дуудах (cancelInv())
        if (this.props.onCancel && typeof this.props.onCancel === 'function') {
            this.props.onCancel();
            this.props.close();
        }
        // Дараа нь ask function-ийн cancel prop-ийг дуудах (popup-ийг хаах)
        if (this.props.cancel && typeof this.props.cancel === 'function') {
            this.props.cancel();
        } else if (this.props.close && typeof this.props.close === 'function') {
            this.props.close();
        } else {
            // Dialog-ийг хаах
            this.dialog.closeAll();
        }
    }

    onDismiss() {
        // dismiss prop-ийг дуудах (cancelInv())
        if (this.props.onDismiss && typeof this.props.onDismiss === 'function') {
            this.props.onDismiss();
        }
        // Dialog-ийг хаах
        if (this.props.close && typeof this.props.close === 'function') {
            this.props.close();
        } else {
            this.dialog.closeAll();
        }
    }
}