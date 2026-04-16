/** @odoo-module */
import { ProductInfoPopup } from "@point_of_sale/app/screens/product_screen/product_info_popup/product_info_popup";
import { patch } from "@web/core/utils/patch";
import { onWillStart } from "@odoo/owl";

patch(ProductInfoPopup.prototype, {
    /**
     * Overrides the setup method of ProductInfoPopup to fetch images before rendering.
     */
    setup() {
        super.setup();
        onWillStart(() => this.getImages());
    },

    /**
     * Fetches product images from the backend using the ORM service.
     * Retrieves image IDs associated with the current product.
     * Updates `this.images_ids` with the fetched image data.
     */
    async getImages() {
        this.images_ids = await this.pos.env.services.orm.searchRead(
            'product.product',
            [['id', '=', this.props.product.id]],
            ['image_ids']
        );
    }
});
