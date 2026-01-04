import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { patch } from "@web/core/utils/patch";
import { PosOrder } from "@point_of_sale/app/models/pos_order";
// import { patch } from "@web/core/utils/patch";

// import { Component } from "@odoo/owl";

// export class Orderline extends Component {
//     static template = "point_of_sale.Orderline";
//     static props = {
//         class: { type: Object, optional: true },
//         line: {
//             type: Object,
//             shape: {
//                 isSelected: { type: Boolean, optional: true },
//                 productName: String,
//                 price: String,
//                 qty: String,
//                 unit: { type: String, optional: true },
//                 unitPrice: String,
//                 discount: { type: String, optional: true },
//                 comboParent: { type: String, optional: true },
//                 oldUnitPrice: { type: String, optional: true },
//                 customerNote: { type: String, optional: true },
//                 internalNote: { type: String, optional: true },
//                 imageSrc: { type: String, optional: true },
//                 packLotLines: { type: Array, optional: true },
//                 price_without_discount: { type: String, optional: true },
//                 taxGroupLabels: { type: String, optional: true },
//                 taxAmount: { type: String, optional: true },
//                 taxName: { type: String, optional: true },
//             },
//         },
//         showTaxGroupLabels: { type: Boolean, optional: true },
//         slots: { type: Object, optional: true },
//         basic_receipt: { type: Boolean, optional: true },
//     };
//     static defaultProps = {
//         class: {},
//         showTaxGroupLabels: false,
//         basic_receipt: false,
//     };
// }


patch(OrderReceipt.prototype, {
    setup() {
        super.setup();
        console.log("🔥 OrderReceipt Patch Applied!", this.props.data);
    },

    /** Override the orderlines getter to inject tax_details */

    get orderlines() {
        const orderlinesWithTax = this.props.data.orderlines.map((line) => {
            const taxDetails = line.tax_details || [];
            return {
                ...line,
                taxAmount: line.tax_amount || line.taxAmount || 0,
                taxName: line.tax_name || line.taxName || '',
                tax_details: taxDetails
            };
        });

        console.log("🔎 Final Orderlines with Tax Details:", orderlinesWithTax);
        return orderlinesWithTax;
    },
});

patch(Orderline.prototype, {
    setup() {
        super.setup();
        console.log("✅ Orderline Patch Applied!", this.props.line);
        this.props.line.taxName = "T23"
        this.props.line.taxAmount = "9"
        // this.props = {
        //     class: { type: Object, optional: true },
        //     line: {
        //         type: Object,
        //         shape: {
        //             isSelected: { type: Boolean, optional: true },
        //             productName: String,
        //             price: String,
        //             qty: String,
        //             unit: { type: String, optional: true },
        //             unitPrice: String,
        //             discount: { type: String, optional: true },
        //             comboParent: { type: String, optional: true },
        //             oldUnitPrice: { type: String, optional: true },
        //             customerNote: { type: String, optional: true },
        //             internalNote: { type: String, optional: true },
        //             imageSrc: { type: String, optional: true },
        //             packLotLines: { type: Array, optional: true },
        //             price_without_discount: { type: String, optional: true },
        //             taxGroupLabels: { type: String, optional: true },
        //             taxAmount: { type: String, optional: true },
        //             taxName: { type: String, optional: true },
        //         },
        //     },
        //     showTaxGroupLabels: { type: Boolean, optional: true },
        //     slots: { type: Object, optional: true },
        //     basic_receipt: { type: Boolean, optional: true },
        // };
        },

    // get taxDetails() {
    //     return this.props.line.tax_details || "taxt";
    // },
    get taxName() {
        return this.props.line.taxName || "T1";
    },

    get taxAmount() {
        return this.props.line.taxAmount || "2.6";
    },
});


// patch(PosOrder.prototype, {
//     setup() {
//         super.setup(...arguments);
//     },

//     export_for_printing(baseUrl, headerData) {
//         const result = super.export_for_printing(...arguments);

//         // ✅ Ensure the order lines exist
//         if (!this.lines || !Array.isArray(this.lines)) {
//             console.error("🚨 No valid order lines found in POS Order!");
//             return result;
//         }

//         // ✅ Transform Orderline data into expected format
//         result.orderlines = this.lines.map((line) => {
//             return {
//                 productName: line.full_product_name || line.product_id[1], // ✅ Ensure string value
//                 price: line.price_subtotal_incl.toFixed(2), // ✅ Convert to string
//                 unitPrice: line.price_unit.toFixed(2), // ✅ Convert to string
//                 qty: line.qty.toString(), // ✅ Ensure it's a string
//                 discount: (line.discount || 0).toString(), // ✅ Ensure it's a string
//                 taxAmount: "12", // ✅ Include tax details
//                 taxName: "T3", // ✅ Include tax details
//             };
//         });

//         // ✅ Count total quantity of items in order
//         result.count = this.lines.length;
//         result.total_qty = this.lines.reduce((sum, line) => sum + line.qty, 0);

//         console.log("📄 Final Order Receipt Data:", result);
//         return result;
//     },
// });
// import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
// import { patch } from "@web/core/utils/patch";

// patch(PosOrderline.prototype, {
//     setup() {
//         super.setup(...arguments);
//     },
//     get_tax_details() {
//         const taxes = this.compute_all_taxes() || [];
//         console.log("🔥 Computed Taxes:", taxes); // Debugging
    
//         return taxes.map(tax => ({
//             name: tax.name,
//             amount: tax.amount.toFixed(2),
//         }));
//     },
//     export_for_printing(baseUrl, headerData) {
//         const result = super.export_for_printing(...arguments);
    
//         // Add tax details to each order line
//         result.orderlines = this.lines.map(line => {
//             return {
//                 ...line.export_for_printing(), // Keep existing line data
//                 tax_details: line.get_tax_details(), // Add tax details
//             };
//         });
    
//         console.log("🚀 FINAL RECEIPT EXPORT:", result); // Debugging
//         return result;
//     },
// });
