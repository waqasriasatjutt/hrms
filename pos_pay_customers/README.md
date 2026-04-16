# HME POS Pay Customers

## Technical Documentation & Debugging Guide

This module extends Odoo Point of Sale to allow processing customer payouts (paying money back to customers) directly from the Partner list. It uses a "Balanced Payout" strategy to ensure compatibility with Odoo's core validation rules for empty orders.

---

## 🛠 Technical Architecture

### 1. POS UI Extension (JS/XML)
The module adds a "Create Payment" button to the partner line side-dropdown.

*   **File:** `static/src/overrides/components/partner_list/partner_line/partner_line.xml`
    *   **XPath:** Extends `point_of_sale.PartnerLine`.
    *   **Logic:** Injects a `<DropdownItem>` that triggers `createCustomerPayment()`.
*   **File:** `static/src/overrides/components/partner_list/partner_line/partner_line.js`
    *   **Function:** `createCustomerPayment()`
    *   **Action:** Closes the dropdown and calls `this.pos.createCustomerPayment(this.props.partner)`.
    *   **Helper:** `payLaterPaymentExists()` checks if a "pay_later" method is available to ensure the balancing logic can proceed.

### 2. Core Logic (JS Middleware)
The main logic resides in a patch to the POS Store.

*   **File:** `static/src/overrides/models/pos_store.js`
    *   **Function:** `createCustomerPayment(partner)`
    *   **Workflow:**
        1.  Uses `makeAwaitable` to trigger Odoo 18 `NumberPopup` (for payout amount).
        2.  Filters available payment methods to exclude "pay_later" for the primary payout method.
        3.  Uses `makeAwaitable` to trigger `SelectionPopup`.
        4.  **Order Setup:** Reuses an empty active order or creates a new one.
        5.  **Balanced Transaction Logic:**
            *   Adds a **Negative** payment line (`set_amount(-X)`) for the selected method (e.g., Cash).
            *   Adds a **Positive** payment line (`set_amount(X)`) for the `pay_later` (Customer Account) method.
        6.  **Flagging:** Sets `newOrder.is_settling_account = true`. This is a critical hook for `pos_general_note` and `pos_settle_due`.
        7.  **Navigation:** Performs `this.showScreen("PaymentScreen")`.

### 3. Odoo Framework Integration
*   **Module Dependencies:** 
    *   `point_of_sale`: Base POS functionality.
    *   `pos_settle_due`: Required for the `is_settling_account` behavioral hooks and account reconciliation.
    *   `pos_general_note`: The module sets the `is_settling_account` flag which triggers the `pos_general_note` logic to print the general note report upon order validation.

---

## 🔍 Debugging & Troubleshooting

### Common Error: `pay_later` Method Missing
The module requires a payment method of type `pay_later` (Customer Account) to be configured in the POS.
*   **Symptoms:** "Configuration Error" popup appears.
*   **Debug:** Check POS settings -> Payment Methods. Ensure a method with "Customer Account" type is added to the Current POS.

### Common Error: Order Not Validating
If the order total is not 0.00, Odoo may block validation.
*   **Logic Check:** In `pos_store.js`, ensure the absolute value of the negative payout line matches exactly the positive balancing line.
*   **Code Reference:** `payment.set_amount(-Math.abs(payoutAmount))` vs `balancingPayment.set_amount(Math.abs(payoutAmount))`.

### Report Not Printing
The general note report is triggered by the `is_settling_account` flag.
*   **Debug:** Verify that `pos_general_note` is installed.
*   **Check:** In the browser console (F12), inspect `pos.get_order().is_settling_account`. It must be `true` before clicking "Validate".

---

## 🚀 Odoo "Doings" (Summary)
| Action | Method | Note |
| :--- | :--- | :--- |
| **Popup Interaction** | `makeAwaitable` | New Odoo 18 standard for async dialogs. |
| **Order Creation** | `pos.add_new_order()` | Standard POS order instantiation. |
| **Payment Injection** | `order.add_paymentline(method)` | Native method for adding payments. |
| **Report Trigger** | `is_settling_account = true` | Hook into `pos_general_note` report action. |
| **Invoicing Suppression** | `set_to_invoice(false)` | Handled by `pos_settle_due` when line count is 0. |

---
**Author:** Ali Muzafar
**Version:** 18.0.1.0.0
