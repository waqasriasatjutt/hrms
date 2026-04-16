/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";
import { PosPayment } from "@point_of_sale/app/models/pos_payment";
import { PosOrder } from "@point_of_sale/app/models/pos_order";

// Global function to load installment data
async function loadInstallmentData(posStore, retryCount = 0) {
    try {
        if (!posStore.env?.services?.orm) {
            if (retryCount < 5) {
                setTimeout(() => loadInstallmentData(posStore, retryCount + 1), 1000);
                return;
            } else {
                // ORM service not available
                return;
            }
        }
        
        // Load cards and installments
        const cardResult = await posStore.env.services.orm.searchRead(
            'account.card',
            [['active', '=', true]],
            ['id', 'name', 'active']
        );
        
        const installmentResult = await posStore.env.services.orm.searchRead(
            'account.card.installment',
            [['active', '=', true]],
            ['id', 'name', 'installment', 'surcharge_coefficient', 'card_id', 'active']
        );
        
        // Store data on posStore
        posStore.account_card = cardResult || [];
        posStore.account_card_installment = installmentResult || [];
        
        console.log('✅ Installment data loaded:', posStore.account_card_installment.length, 'installments for', posStore.account_card.length, 'cards');
        console.log('📋 Installment data details:', posStore.account_card_installment.map(i => ({id: i.id, name: i.name, card_id: i.card_id})));
        
    } catch (error) {
        console.error('Error loading installment data:', error);
    }
}

patch(PosPayment.prototype, {
    setup(vals) {
        super.setup(...arguments);
        this.instalment = vals.instalment || false;
    }
});

// Patch to fix change calculation only for receipt
patch(PosOrder.prototype, {
    get_change() {
        // Calculate total surcharge from installment payments
        let totalSurcharge = 0;
        for (const payment of this.payment_ids) {
            if (payment.surcharge_coefficient && payment.surcharge_coefficient > 1) {
                const surcharge = payment.amount * (payment.surcharge_coefficient - 1);
                totalSurcharge += surcharge;
            }
        }
        
        // If there are surcharges, adjust the calculation
        if (totalSurcharge > 0) {
            const adjustedTotal = this.get_total_with_tax() + totalSurcharge;
            const totalPaid = this.get_total_paid();
            const change = totalPaid - adjustedTotal;
            return Math.max(0, change);
        }
        
        // Use original calculation if no surcharges
        return super.get_change();
    }
});

patch(PosStore.prototype, {
    async setup(env, services) {
        // Call the original setup first
        await super.setup(env, services);
        
        // Initialize arrays
        this.account_card_installment = [];
        this.account_card = [];
        
        // Load installment data
        await loadInstallmentData(this);
    },

    captureChange(event) {
        console.log('🔥 CAPTURE CHANGE CALLED - Selected value:', event.target.value);
        const order = this.get_order();
        const selectedInstallmentId = parseInt(event.target.value);
        
        if (!this.account_card_installment || !order) {
            console.log('❌ Missing data - installments:', !!this.account_card_installment, 'order:', !!order);
            return;
        }
        
        const selectedPaymentLine = order.get_selected_paymentline();
        if (!selectedPaymentLine) {
            console.log('❌ No payment line selected');
            return;
        }
        
        // Skip if payment method doesn't have card associated
        if (!selectedPaymentLine.payment_method_id.card_id) {
            console.log('❌ Payment method has no card associated - skipping installment');
            return;
        }
        
        const selectedInstallment = this.account_card_installment.find(inst => inst.id === selectedInstallmentId);
        console.log('🎯 Selected installment found:', selectedInstallment);

        if (selectedInstallment) {
            // Store installment info on payment line and order
            selectedPaymentLine.installment_id = selectedInstallment.id;
            selectedPaymentLine.instalment_id = `INSTALLMENT:${selectedInstallment.id}`;  // Note: different field name
            selectedPaymentLine.ticket = `Cuotas:${selectedInstallment.name}`;  // Use ticket field as carrier
            selectedPaymentLine.instalment = selectedInstallment.id;  // Use ticket field as carrier
            order.installment_id = selectedInstallment.installment;
            order.surcharge_coefficient = selectedInstallment.surcharge_coefficient;
            
            console.log('✅ Stored installment_id:', selectedInstallment.id, 'on payment line and order:', selectedInstallment.installment);
            console.log('✅ Nombre de cuota:', selectedInstallment.name);
            console.log('📋 Payment line details:', {
                installment_id: selectedPaymentLine.installment_id,
                instalment_id: selectedPaymentLine.instalment_id,
                amount: selectedPaymentLine.amount,
                payment_method_id: selectedPaymentLine.payment_method_id.id
            });
            
            // Update payment line amount with surcharge coefficient
            // const originalAmount = selectedPaymentLine.amount / (selectedPaymentLine.surcharge_coefficient || 1);
            // selectedPaymentLine.amount = originalAmount * selectedInstallment.surcharge_coefficient;
            selectedPaymentLine.surcharge_coefficient = selectedInstallment.surcharge_coefficient;
            
            console.log('Installment applied:', selectedInstallment.installment, 'cuotas, coefficient:', selectedInstallment.surcharge_coefficient);
        }
    },

});

console.log('✅ INSTALLMENT PATCH APPLIED SUCCESSFULLY - pos_simple.js ready');