import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";

patch(ProductScreen.prototype, {

    getProductName(product) {
        var result = super.getProductName(...arguments);
        if (product.default_code) {
            result = result + " " + "[" + product.default_code + "]"
        } 
        return result
    }

});
