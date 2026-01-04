/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { formatCurrency } from "@point_of_sale/app/models/utils/currency";

// Patch PosOrderline
patch(PosOrderline.prototype, {

	get_all_prices(qty = this.get_quantity()) {
        // Call the original method using this._super()
        const prices = super.get_all_prices(...arguments);
        // Extend taxDetails by adding the `name` property
        if (prices.taxDetails && prices.taxesData) {
            for (const taxData of prices.taxesData) {
                if (prices.taxDetails[taxData.id]) {
                    prices.taxDetails[taxData.id].name = taxData.name; // Add name to taxDetails
                }
            }
        }
        return prices;
    },

    getDisplayData() {
		const taxDetails = this.get_tax_details();
		const taxesArray = Object.values(taxDetails).map(tax => ({
			name: tax.name || "",
			amount: formatCurrency(tax.amount, this.currency),
		}));

		return {
			...super.getDisplayData(),
			taxes: taxesArray, // Store an array of tax objects
		};
	},
});

// Patch the shape of Orderline
patch(Orderline, {
	props: {
		...Orderline.props,
		line: {
			...Orderline.props.line,
			shape: {
				...Orderline.props.line.shape,
				taxes: { type: Array, optional: true },
			},
		},
	},
});
