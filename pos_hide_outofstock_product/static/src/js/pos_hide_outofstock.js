/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";

console.log("🟣 pos_hide_outofstock module loaded");

patch(PosStore.prototype, {
    async afterProcessServerData() {
        const res = await super.afterProcessServerData?.(...arguments);

        const products = this.models["product.product"].getAll();
        if (!products.length) return res;

        const product_ids = products.map(p => p.id);

        try {
            const qty_data = await this.data.call(
                "product.product",
                "read",
                [product_ids, ["qty_available"]]
            );

            qty_data.forEach((prod) => {
                const localProd = this.models["product.product"].get(prod.id);
                if (localProd) localProd.raw.qty_available = prod.qty_available ?? 0;
            });

            console.log(`📦 Total products loaded: ${products.length}`);
        } catch (err) {
            console.error("❌ Error fetching qty_available:", err);
        }

        return res;
    },
});

patch(ProductScreen.prototype, {
    __debugLogged: false,  

    get productsToDisplay() {
        let list = [];

        if (this.searchWord) {
            list = this.addMainProductsToDisplay(
                this.getProductsBySearchWord(this.searchWord)
            );
        } else if (this.pos.selectedCategory?.id) {
            list = this.getProductsByCategory(this.pos.selectedCategory);
        } else {
            list = this.products;
        }

        const totalBeforeFilter = list.length;

        let hiddenCount = 0;
        if (this.pos.config.hide_outofstock_products) {
            const beforeFilterCount = list.length;
            list = list.filter(p => Number(p.raw.qty_available || 0) > 0);
            hiddenCount = beforeFilterCount - list.length;
        }

        const totalAfterFilter = list.length;

        const excludedIds = [
            this.pos.config.tip_product_id?.id,
            ...(this.pos.hiddenProductIds || []),
            ...(this.pos.session._pos_special_products_ids || []),
        ];

        const finalList = list.filter(p => !excludedIds.includes(p.id) && p.available_in_pos);

        // Log debug only once
        if (!this.__debugLogged) {
            console.log(`🧮 Products before out-of-stock filter: ${totalBeforeFilter}`);
            console.log(`🚫 Products hidden (out of stock): ${hiddenCount}`);
            console.log(`✅ Products after filtering: ${totalAfterFilter}`);
            console.log(`🎯 Final products to display (after exclusions): ${finalList.length}`);
            this.__debugLogged = true;
        }

        return finalList;
    },
});
