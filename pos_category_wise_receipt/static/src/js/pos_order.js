import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

// Patching PosOrder for getting the category of the added products
patch(PosOrder.prototype, {
    // Extending export_for_printing function to return orderlines with its category
    export_for_printing(baseUrl, headerData) {
        const lines = [...this.get_orderlines()];
        const groupedObjects = lines.reduce((acc, line) => {
            const { product_id } = line;
            if (product_id.pos_categ_ids && product_id.pos_categ_ids.length > 0) {
                const categoryId = product_id.pos_categ_ids[0];
                const categoryName = categoryId.name;
                if (!acc[categoryName]) {
                    acc[categoryName] = { category_name: categoryName, lines: [] };
                }
                acc[categoryName].lines.push(line);
            }
            return acc;
        }, {});
        const result = Object.values(groupedObjects);
        const orderlines = super.export_for_printing(...arguments);
        return {
            ...orderlines,
            orderlines: result
        }
    },
});
