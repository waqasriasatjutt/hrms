/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { usePos } from "@point_of_sale/app/store/pos_hook";

patch(ProductScreen.prototype, {
    setup() {
        super.setup(...arguments);
          this.pos = usePos();
    },
    get productsToDisplay() {
        const products = super.productsToDisplay;
        return [...products].sort((a, b) => {
            const seqA = a.product_tmpl_id?.pos_sequence || 0;
            const seqB = b.product_tmpl_id?.pos_sequence || 0;

            return seqA - seqB;
        });
    },
});
