/** @odoo-module */

/*
 * Copyright (C) 2025 Axcelere.
 * Licensed under the GPL-3.0 License or later.
 */

import { register_payment_method } from "@point_of_sale/app/store/pos_store";
import { PaymentMpqr } from "@pos_mercadopagoqr/js/payment_mpqr";

register_payment_method("mpqr", PaymentMpqr);
