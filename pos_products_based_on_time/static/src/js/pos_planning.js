/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";

patch(ProductScreen.prototype, {
		/**
		 * Override the productsToDisplay getter method to filter the list of products
		 * based on the current time and the meals planning data.
		 * @returns {Array} A sorted array of product objects to be displayed.
		 */
        get productsToDisplay() {
            let list = [];
            // Step 1: Get the products based on search or selected category
            if (this.searchWord !== "") {
                list = this.getProductsBySearchWord(this.searchWord);
            } else if (this.pos.selectedCategory?.id) {
                list = this.getProductsByCategory(this.pos.selectedCategory);
            } else {
                list = this.products;
            }
            // Step 2: If no products, return empty list
            if (!list) {
                return [];
            }
            // Step 3: Filter products based on availability and hidden status
            list = list
                .filter(
                    (product) =>
                        ![
                            this.pos.config.tip_product_id?.id,
                            ...this.pos.hiddenProductIds,
                            ...this.pos.session._pos_special_products_ids,
                        ].includes(product.id) && product.available_in_pos
                )
                .slice(0, 100);

            // Step 4: Get current time in minutes since midnight
            const date = new Date();
            const timeInMinutes = date.getHours() * 60 + date.getMinutes();  // Convert time to minutes since midnight
            let data = [];
            // Step 5: Loop through meals planning and filter based on time
            this.env.services.pos.meals_planning.forEach(object => {
                // Convert object time to minutes since midnight
                const timeFromInMinutes = object.time_from * 60; // assuming time_from is in hours
                const timeToInMinutes = object.time_to * 60; // assuming time_to is in hours

                // Check if current time is within the meal planning time range
                if (timeFromInMinutes <= timeInMinutes && timeInMinutes < timeToInMinutes) {
                    const planArr = object.menu_product_ids.flat(1); // Flatten the menu product IDs
                    data.push(planArr.map(meal => meal.id)); // Push the meal IDs to the data array
                }
            });
			if (data.length) {
				list = list.filter(product => data[0].includes(product.id))
			}
        return this.searchWord !== ""
            ? list
            : list.sort((a, b) => a.display_name.localeCompare(b.display_name));
    }
});
