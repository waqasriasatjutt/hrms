/** @odoo-module */
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

patch(PosOrder.prototype, {
    export_for_printing(baseUrl, headerData) {
        const result = super.export_for_printing(...arguments);

        // Add customer details (existing logic)
        if (this.partner_id) {
            result.headerData.customer_name = this.partner_id.name;
            result.headerData.customer_address = this.partner_id.contact_address;
            result.headerData.customer_mobile = this.partner_id.mobile;
            result.headerData.customer_phone = this.partner_id.phone;
            result.headerData.customer_email = this.partner_id.email;
            result.headerData.customer_vat = this.partner_id.vat;
        }

        // ✅ Detect NearPay via terminal type + presence of NearPay fields
        const nearpayPayments = this.payment_ids.filter(payment =>
            payment.nearpay_transaction_id || 
            (payment.payment_method_id?.payment_method_type === 'terminal' && 
             payment.nearpay_card_scheme) // extra safety: ensure it's NearPay
        );

        if (nearpayPayments.length > 0) {
            const p = nearpayPayments[0];
            result.headerData.nearpay_data = {
                card_scheme: p.nearpay_card_scheme || 'CARD',
                approval_code: p.nearpay_approval_code,
                transaction_id: p.nearpay_transaction_id,
                amount: p.nearpay_amount_authorized || p.amount,
                currency: p.nearpay_currency || 'SAR',
                status: p.nearpay_status_message || 'Approved',
                card_number: p.nearpay_card_number,
                expiry: p.nearpay_expiry,
                terminal_id: p.nearpay_terminal_id,
                merchant_id: p.nearpay_merchant_id,
                retrieval_ref_no: p.nearpay_retrieval_ref_no,
            };
        } else {
            result.headerData.nearpay_data = null;
        }

        return result;
    },
});