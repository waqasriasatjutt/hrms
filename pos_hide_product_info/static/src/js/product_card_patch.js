/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { ProductCard } from "@point_of_sale/app/generic_components/product_card/product_card";
import { usePos } from "@point_of_sale/app/store/pos_hook";

patch(ProductCard.prototype, {
    setup() {
        super.setup();
        this.pos = usePos();
        if (this.pos.config && this.pos.config.pos_hide_product_info) {
            this.props.productInfo = false;
        }
    },
});
