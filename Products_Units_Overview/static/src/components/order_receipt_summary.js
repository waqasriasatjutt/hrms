import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { patch } from "@web/core/utils/patch";

patch(OrderReceipt.prototype, {
    get ItemCount() {
    const totalQuantity = this.props.data.orderlines.reduce((sum, orderLine) => {
        return sum + parseFloat(orderLine.qty);
    }, 0);
    return totalQuantity;
    }
});
