import { _t } from "@web/core/l10n/translation";
import { Dialog } from "@web/core/dialog/dialog";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

//MassEditPopup component
export class MassEditPopup extends Component {
    static template = "pos_order_line_mass_edit.MassEditPopup";
    static components = { Dialog };
    static defaultProps = {
        title: _t("Edit order lines"),
        confirmLabel: _t("Confirm"),
        cancelLabel: _t("Cancel"),
        confirmClass: "btn-primary",
    };
    static props = {
        close: Function,
        body: { type: Object, optional: true },
        confirm: { type: Function, optional: true },
        confirmLabel: { type: String, optional: true },
        confirmClass: { type: String, optional: true },
        cancel: { type: Function, optional: true },
        cancelLabel: { type: String, optional: true },
    };
    setup(){
        this.pos = usePos();
    }
    async updateQty(line, value) {
        const qty = parseFloat(value);
        if (!isNaN(qty)) {
            line.qty = qty;
        } else {
            console.error("Invalid quantity input:", value);
        }
    }
    async _cancel() {
        this.props.close();
        window.location.reload();
    }
    async _confirm() {
        this.props.close();
    }
    sendInput(key) {
        this.props.body.forEach((order) => {
            if (order.id == key) {
                var current_order = this.pos.get_order()
                current_order.removeOrderline(order)
            }
        })
    }
}