// /** @odoo-module **/

// import { patch } from "@web/core/utils/patch";
// import { changesToOrder } from "@point_of_sale/app/models/utils/order_change";

// patch(changesToOrder, {
//     __call__(original, order, skipped = false, orderPreparationCategories, cancelled = false) {
//         const result = original(order, skipped, orderPreparationCategories, cancelled);

//         // 🔥 Single source of truth for kitchen receipt
//         result.sittingMode =
//             order.last_order_preparation_change?.sittingMode || "dine in";

//         return result;
//     },
// });
