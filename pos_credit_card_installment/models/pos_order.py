from odoo import api, fields, models, tools, _

import logging

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def _process_order(self, order, existing_order):
        # Check payment_ids for installment info
        if order.get('payment_ids'):
            payment_data = order['payment_ids'][0][2]  # Get payment data directly
            # Check if installment info is in ticket field
            instalment = payment_data.get('instalment', '')
            if instalment:
                installment_id_from_ticket = instalment
                
                # Process the installment
                installment = self.env['account.card.installment'].browse(installment_id_from_ticket)
                payment_method_id = order['payment_ids'][0][2]['payment_method_id']
                payment_method_id = self.env['pos.payment.method'].browse(payment_method_id)
                
                if installment.exists() and payment_method_id.instalment_product_id:
                    # Calculate surcharge amount (difference between new amount and original)
                    original_total = order['amount_total']
                    surcharge_total_with_tax = (original_total * installment.surcharge_coefficient) - original_total
                    
                    # Get tax information from the installment product
                    installment_product = payment_method_id.instalment_product_id
                    tax_ids = installment_product.taxes_id.ids
                    
                    # Calculate price_unit without taxes
                    if tax_ids:
                        # Get the tax rate (assuming single tax for simplicity)
                        tax = self.env['account.tax'].browse(tax_ids[0])
                        tax_rate = tax.amount / 100.0
                        # price_unit = surcharge_total_with_tax / (1 + tax_rate)
                        price_unit = surcharge_total_with_tax / (1 + tax_rate)
                        price_subtotal = price_unit
                        price_subtotal_incl = surcharge_total_with_tax
                    else:
                        price_unit = surcharge_total_with_tax
                        price_subtotal = surcharge_total_with_tax
                        price_subtotal_incl = surcharge_total_with_tax
                    
                    # Add the surcharge line to the order
                    surcharge_line = {
                        'name': f"Recargo por cuotas - {installment.name}",
                        'full_product_name': installment_product.display_name,
                        'price_unit': price_unit,
                        'product_id': installment_product.id,
                        'qty': 1,
                        'discount': 0,
                        'price_subtotal': price_subtotal,
                        'price_subtotal_incl': price_subtotal_incl,
                        'tax_ids': tax_ids,
                        'pack_lot_ids': [],
                    }
                    
                    order['lines'].append((0, 0, surcharge_line))
                    
                    # Update order totals
                    order['amount_tax'] = order.get('amount_tax', 0) + (price_subtotal_incl - price_subtotal)
                    order['amount_total'] = order.get('amount_total', 0) + price_subtotal_incl
                    
                    # Update payment amount to reflect the surcharge
                    new_payment_amount = original_total * installment.surcharge_coefficient
                    payment_data['amount'] = new_payment_amount
                    order['amount_paid'] = new_payment_amount
        
        res = super(PosOrder, self)._process_order(order, existing_order)
        return res