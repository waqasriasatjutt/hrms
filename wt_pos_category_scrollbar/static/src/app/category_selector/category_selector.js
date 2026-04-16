import { CategorySelector } from "@point_of_sale/app/generic_components/category_selector/category_selector";
import { onMounted, useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { patch } from "@web/core/utils/patch";

patch(CategorySelector.prototype, {
	setup() {
		super.setup()
        if(!this.pos){
        	this.pos = usePos();
        }
		if(!this.state){
			this.state = useState({})
		}
        onMounted(() => {
            this.state.category_scroll_width = this.calculateCategoryScrollWidth();
        });
        this.state.category_scroll_height = this.pos.config.iface_big_scrollbars ? 7 : 6;
	},
	calculateCategoryScrollWidth(){
		const width = document.getElementsByClassName('wt_category_identify_cl')[0]?.offsetWidth || 1010;
        return width - 10
	}
});