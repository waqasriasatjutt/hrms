/** @odoo-module */
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";
import { useState } from "@odoo/owl";

patch(PosOrder.prototype, {
       setup(){
       super.setup(...arguments);
       },
       export_for_printing(baseUrl, headerData) {
           const result = super.export_for_printing(...arguments);
          result.count = this.lines.length
          this.receipt = result.count
          var sum = 0;
          this.lines.forEach(function(t) {
                    sum += t.qty;
                })
                result.sum = sum
                return result;
       },
});