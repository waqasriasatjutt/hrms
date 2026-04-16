/** @odoo-module */

import {Component, useState} from "@odoo/owl";
import {Dialog} from "@web/core/dialog/dialog";
import {formatDateTime} from "@web/core/l10n/dates";
import {parseUTCString} from "@point_of_sale/utils";
import {usePos} from "@point_of_sale/app/store/pos_hook";
import {useService} from "@web/core/utils/hooks";

export class OrderDetailsPopup extends Component {
    setup() {
        // Inherit the method to initialize variables. #T8407
        super.setup();
        this.pos = usePos();
        this.ui = useState(useService("ui"));
        this.dialog = useService("dialog");
    }

    getDate() {
        // New method to get order date. #T6479
        return formatDateTime(parseUTCString(this.props.order.date_order));
    }

    getTotal() {
        // New method to get total with tax. #T6479
        return this.env.utils.formatCurrency(this.props.order.get_total_with_tax());
    }

    // Change the method name. #T8407
    getPriceExclTax(line) {
        // New method to get price without tax. #T6479
        return this.env.utils.formatCurrency(line.get_price_without_tax());
    }

    // Change the method name. #T8407
    getPriceInclTax(line) {
        // New method to get price with tax. #T6479
        return this.env.utils.formatCurrency(line.get_price_with_tax());
    }

    getCashier() {
        // New method to get Cashier name. #T8407
        return this.props.order.employee_id ? this.props.order.employee_id.name : "";
    }

    getTax(line) {
        // New method to get tax value. #T6479
        if (line.tax_ids && line.tax_ids.length > 0) {
            return line.tax_ids.map((tax) => tax.name);
        }
        return [];
    }

    getDiscount(line) {
        // New method to get discount value. #T8407
        return line.discount ? line.discount.toFixed(1) : "0.00";
    }

    formatDecimal(number) {
        // New Method to format a number to two decimal places. #T8407
        return typeof number === "number" ? number.toFixed(2) : "0.00";
    }

    getPricelist() {
        // New Method to get a pricelist value. #T8407
        return this.props.order.pricelist_id
            ? this.props.order.pricelist_id.display_name
            : "";
    }
}

// Set static properties for the template and components. #T8407
OrderDetailsPopup.template = "OrderDetailsPopup";
OrderDetailsPopup.components = {Dialog};
