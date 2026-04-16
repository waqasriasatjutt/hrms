import { Chrome } from "@point_of_sale/app/pos_app";
import { patch } from "@web/core/utils/patch";

patch(Chrome.prototype, {
  setup() {
    super.setup();
    this.pos.chrome = this;
  },
});
