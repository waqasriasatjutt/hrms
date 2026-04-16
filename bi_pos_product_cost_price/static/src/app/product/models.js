/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosOrder } from "@point_of_sale/app/models/pos_order";

patch(PosOrder.prototype, {

    setup(vals) {
        super.setup(vals);
        this.SearchCostPriceOrder = this.get_SearchCostPriceOrder || 0;
        
    },

    set_SearchCostPriceOrder(SearchCostPriceOrder){
        this.SearchCostPriceOrder = SearchCostPriceOrder;
    },

    get_SearchCostPriceOrder() {
        return this.SearchCostPriceOrder;
    },

    export_for_printing() {
        const json = super.export_for_printing(...arguments);
        json.SearchCostPriceOrder = this.get_SearchCostPriceOrder();
        return json;
    },
});




