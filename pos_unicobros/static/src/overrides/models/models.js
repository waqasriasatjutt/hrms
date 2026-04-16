/** @odoo-module */
import { register_payment_method } from "@point_of_sale/app/store/pos_store";
import { PaymentUnicobros } from "@pos_unicobros/app/payment_unicobros";

register_payment_method("unicobros", PaymentUnicobros);
