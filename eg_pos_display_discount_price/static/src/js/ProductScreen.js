/** @odoo-module **/

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { session } from "@web/session";
import { OrderWidget } from "@point_of_sale/app/generic_components/order_widget/order_widget";
import { patch } from "@web/core/utils/patch";

patch(ProductScreen.prototype, {
        async addProductToOrder(product, options = {}) {
            var self = this;
            if(this.pos.config.display_discount_price && product.discount_price > 0){
                    var discount_price = product.discount_price
                    product.lst_price = discount_price;
                     super.addProductToOrder(...arguments);
            }else{
                 super.addProductToOrder(...arguments);
            }
        }
});

