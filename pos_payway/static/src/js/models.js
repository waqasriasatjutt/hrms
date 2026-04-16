/** @odoo-module */

/*
 * Copyright (C) 2024 Axcelere.
 * Licensed under the GPL-3.0 License or later.
 */

import { register_payment_method } from "@point_of_sale/app/store/pos_store";
import { PaymentPayway } from "@pos_payway/js/payment_payway";

register_payment_method("payway", PaymentPayway);
