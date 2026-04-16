/** @odoo-module **/

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { rpc } from "@web/core/network/rpc";
import { onMounted } from "@odoo/owl";

patch(ProductScreen.prototype, {
    setup() {
        // Call the original setup
        super.setup();
        onMounted(() => {
            this.pos.openOpeningControl();
            this.numberBuffer.reset();
            this.reloadProductPinStatus();
        });
    },

    async reloadProductPinStatus() {
        const templates = await this.pos.data.searchRead(
            "product.template",
            [],
            ["id", "is_pin_product"]
        );
        const pinMap = {};
        for (const tmpl of templates) {
            pinMap[tmpl.id] = tmpl.is_pin_product;
        }
        const products = this.pos.models["product.product"].getAll();
        for (const product of products) {
            const tmplId = product.product_tmpl_id || (product.raw && product.raw.product_tmpl_id);
            const templateId = Array.isArray(tmplId) ? tmplId[0] : tmplId;
            if (templateId && pinMap.hasOwnProperty(templateId)) {
                product.is_pin_product = pinMap[templateId];
            }
        }
    },

    get productsToDisplay() {
        let list = [];
        if (this.searchWord !== "") {
            if (!this._searchTriggered) {
                this.pos.setSelectedCategory(0);
                this._searchTriggered = true;
            }
            list = this.addMainProductsToDisplay(this.getProductsBySearchWord(this.searchWord));
        } else {
            this._searchTriggered = false;
            if (this.pos.selectedCategory?.id) {
                list = this.getProductsByCategory(this.pos.selectedCategory);
            } else {
                list = this.products;
            }
        }
        if (!list || list.length === 0) {
            return [];
        }
        const excludedProductIds = [
            this.pos.config.tip_product_id?.id,
            ...this.pos.hiddenProductIds,
            ...this.pos.session._pos_special_products_ids,
        ];
        const filteredList = [];
        for (const product of list) {
            if (filteredList.length >= 100) {
                break;
            }
            if (!excludedProductIds.includes(product.id) && product.canBeDisplayed) {
                filteredList.push(product);
            }
        }
        return this.searchWord !== ""
            ? filteredList.sort((a, b) => (b.is_pin_product === true) - (a.is_pin_product === true) || a.display_name.localeCompare(b.display_name))
            : filteredList.sort((a, b) => (b.is_pin_product === true) - (a.is_pin_product === true) || a.display_name.localeCompare(b.display_name));
    },
    async onTogglePin(product) {
        const tmplField = product.product_tmpl_id || product.raw?.product_tmpl_id;
        const templateId = Array.isArray(tmplField) ? tmplField[0] : tmplField;

        if (!templateId) {
            this.notification.add(_t("Could not determine product template ID."), {
                type: "danger",
            });
            return;
        }
        let newValue = !product.is_pin_product

        try {
            await rpc("/pos/pin_product", {
                template_id: templateId,
                new_value: newValue,
            });
            product.is_pin_product = newValue;
        } catch (error) {
            console.error("Toggle failed:", error);
            this.notification.add(_t("Could not update pin status."), {
                type: "danger",
            });
        }
    }
});