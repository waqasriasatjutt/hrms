/** @odoo-module */
import { register_payment_method } from "@point_of_sale/app/store/pos_store";
import { PaymentCompago } from "@pos_compago/app/payment_compago";

register_payment_method("compago", PaymentCompago);
