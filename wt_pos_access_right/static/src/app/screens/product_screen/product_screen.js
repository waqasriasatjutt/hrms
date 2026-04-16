import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";
import { onMounted } from "@odoo/owl";


patch(ProductScreen.prototype, {
	getNumpadButtons() {
		const result = super.getNumpadButtons()
		
		const is_restrict_quantity = this.pos.get_cashier()._is_restrict_quantity
		const is_restrict_discount = this.pos.get_cashier()._is_restrict_discount
		const is_restrict_backspace = this.pos.get_cashier()._is_restrict_remove_line
		const is_restrict_plus_minus = this.pos.get_cashier()._is_restrict_plus_minus

		result.forEach((button) => {
			if(button.value === 'quantity' && is_restrict_quantity){
				button.disabled = true
			}
			if(button.value === 'discount' && is_restrict_discount){
				button.disabled = true
			}
			if(button.value === 'Backspace' && is_restrict_backspace){
				button.disabled = true
			}
			if(button.value === '-' && is_restrict_plus_minus){
				button.disabled = true
			}
		});
		return result
	}
	
});