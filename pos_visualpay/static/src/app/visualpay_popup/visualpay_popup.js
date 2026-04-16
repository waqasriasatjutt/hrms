import { Component, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class VisualPayPopup extends Component {
    static template = "pos_visualpay_popup.VisualPayPopup";
    static components = { Dialog };
    static props = {
        lines: Array,
        order: Object,
        onConfirm: Function,
        onCancel: Function,
        close: Function,
    };

    setup() {
        this._t = _t;
        this.notification = useService("notification");
        this.state = useState({
            currentTab: 0,
            evidences: (this.props.lines || []).map(() => ({
                preview: null,
                imageBase64: null,
                comment: "",
            })),
            pendingFileTab: null,
        });
    }

    get currentLine() {
        const idx = this.state.currentTab;
        const line = (this.props.lines && this.props.lines[idx]) || null;
        return line;
    }

    get currentEv() {
        const idx = this.state.currentTab;
        const ev = (this.state.evidences && this.state.evidences[idx]) || { preview: null, imageBase64: null, comment: "" };
        return ev;
    }

    onTabChange(index) {
        index = Number(index);
        if (isNaN(index) || index < 0 || index >= (this.props.lines || []).length) {
            return;
        }
        this.state.currentTab = index;
    }

    triggerFileInput(idx) {
        idx = idx ?? this.state.currentTab;
        this.state.pendingFileTab = idx;
        const input = document.getElementById("globalFileInput");
        if (input) {
            input.click();
        }
    }

    onImageChange(ev) {
        const file = ev.target.files?.[0];
        if (!file) return;

        const idx = this.state.pendingFileTab ?? this.state.currentTab;
        const reader = new FileReader();

        reader.onload = (e) => {
            if (!this.state.evidences[idx]) this.state.evidences[idx] = { preview: null, imageBase64: null, comment: "" };
            this.state.evidences[idx].preview = e.target.result;
            this.state.evidences[idx].imageBase64 = e.target.result.split(",")[1];
            ev.target.value = ""; // Limpia input
            this.state.pendingFileTab = null; // Resetea pestaña temporal
        };

        reader.readAsDataURL(file);
    }

    removeImage() {
        const idx = this.state.currentTab;
        if (this.state.evidences[idx]) {
            this.state.evidences[idx].preview = null;
            this.state.evidences[idx].imageBase64 = null;
        }
    }

    onCommentInput(ev) {
        const idx = this.state.currentTab;
        if (!this.state.evidences[idx]) this.state.evidences[idx] = { preview: null, imageBase64: null, comment: "" };
        this.state.evidences[idx].comment = ev.target.value;
    }

    confirmAll() {
        for (let i = 0; i < (this.props.lines || []).length; i++) {
            const line = this.props.lines[i];
            const ev = this.state.evidences[i] || {};
            if (line?.payment_method_id?.visualpay_require_confirmation && !ev.imageBase64) {
                this.notification.add(
                    `Debe subir una imagen de evidencia para ${line.payment_method_id.name}.`,
                    { type: "warning" }
                );
                return;
            }
        }

        const dataList = (this.props.lines || []).map((line, i) => ({
            line_id: line.id,
            name: line.payment_method_id.name,
            image: (this.state.evidences[i] || {}).imageBase64,
            comment: (this.state.evidences[i] || {}).comment,
        }));

        if (this.props.onConfirm) this.props.onConfirm(dataList);
        if (this.props.close) this.props.close();
        else if (this.env.dialog) this.env.dialog.close();
    }

    cancelAll() {
        if (this.props.onCancel) this.props.onCancel();
        if (this.props.close) this.props.close();
        else if (this.env.dialog) this.env.dialog.close();
    }
}
