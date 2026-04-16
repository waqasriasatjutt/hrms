/** @odoo-module **/

import { ProductProduct } from "@point_of_sale/app/models/product_product";
import { patch } from "@web/core/utils/patch";

patch(ProductProduct.prototype, {
    get searchString() {
        // const result = super.searchString();
        const fields = ["display_name", "barcode", "default_code", "vendor_product_name", "vendor_product_code"];
        return fields
            .map((field) => this[field] || "")
            .filter(Boolean)
            .join(" ");
    }
});
