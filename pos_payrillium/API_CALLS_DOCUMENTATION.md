# 📡 Payrillium API Calls Documentation

## Overview

This document explains all API calls made to Mirillium API from the Payrillium module, both from POS (Point of Sale) and Invoice contexts.

---

## 🌐 Mirillium API Endpoints

### Base URLs
- **ShopNet API**: `https://sn.mirillium.io` (for terminal management)
- **Payment API (Dev)**: `https://mqtt-p100.mirillium.io/cloud-payment-vpc/` (for payments)
- **Payment API (Prod)**: `https://cloud.mirillium.net/cloud-payment-vpc/` (for payments)

### Authentication
- All requests use **HMAC SHA-256** signatures
- Secret key is encrypted at rest (XOR + Base64)
- API token is validated before use

---

## 🔄 API Calls from Backend (Python)

### 1. Terminal Management (Invoice Configuration)

**Endpoint:** `GET https://sn.mirillium.io/api/v1/get_terminals_by_customer`

**Called From:**
- `models/payrillium_wizard.py` → `submit_token()`
- Used during Payrillium configuration wizard

**When:** User configures Payrillium token in Odoo settings

**Purpose:** Fetch list of available payment terminals for the merchant

**What is Sent:**
```python
{
    "code": "A105",  # First 4 chars of token
    "token": "6193354076942470"  # Rest of token
}
```

**What is Received:**
```python
{
    "success": True,
    "data": [
        {
            "name": "Terminal Name",
            "serial": "2210061669",
            "gateway": "Gateway Type"
        }
    ],
    "mirillium_config": {
        "code": "merchant_id",
        "secret_key": "encrypted_secret",
        "pbl_developer_id": "...",
        "pbl_solution_id": "...",
        "pbl_request_phone": false,
        "pbl_request_shipping": false
    }
}
```

**What Happens:**
- Terminals are synchronized in Odoo
- Merchant ID and secret key are stored (secret key encrypted)
- Pay-by-Link configuration is stored

---

### 2. Payment Link Creation (Invoice)

**Endpoint:** `POST https://mqtt-p100.mirillium.io/cloud-payment-vpc/api/v1/payment/links`

**Called From:**
- `services/mirillium/api.py` → `create_payment_link()`
- `controllers/main.py` → `generate_link()` endpoint
- Used when user generates payment link from invoice

**When:** User clicks "Generate Payment Link" button on invoice

**Purpose:** Create a payment link that customer can use to pay invoice

**What is Sent:**
```python
{
    "purchaseNumber": "INV1234A1",
    "totalAmount": "100.00",
    "currency": "USD",
    "invoice": {
        "number": "INV/2024/0001",
        "customer": "Customer Name",
        "amount": "100.00"
    },
    # ... other invoice details
}
```

**What is Received:**
```python
{
    "success": True,
    "data": {
        "id": "link_id",
        "url": "https://pay.mirillium.io/pay/ABC123",
        "status": "active"
    }
}
```

**What Happens:**
- Payment link is created in Mirillium
- Link is stored in `payrillium.payment.link` model
- Link is copied to clipboard
- Link is added to invoice chatter

---

### 3. Payment Token Creation (Invoice - Save Card)

**Endpoint:** `POST https://mqtt-p100.mirillium.io/cloud-payment-vpc/api/v1/tokens/payment_instrument`

**Called From:**
- `services/mirillium/api.py` → `create_payment_token()`
- `models/payment_token_wizard.py` → `action_generate_token()`
- Used when user saves card token from invoice

**When:** User clicks "Pay by Token" → "Save Card" on invoice

**Purpose:** Create a tokenized payment instrument (card or ACH) for future payments

**What is Sent:**
```python
{
    "type": "CARD",  # or "CHECK"
    "card": {
        "number": "4111111111111111",  # NEVER logged
        "expirationMonth": "12",
        "expirationYear": "25",
        "securityCode": "123"  # NEVER logged
    }
    # OR
    "check": {
        "accountNumber": "...",
        "routingNumber": "..."
    }
}
```

**⚠️ SECURITY:** Card data is **NEVER logged** (PCI compliance)

**What is Received:**
```python
{
    "success": True,
    "data": {
        "token": "TOKEN_REFERENCE_ONLY"  # Not full card data
    }
}
```

**What Happens:**
- Token reference is stored in `payment.token` model
- **Full card data is NOT stored** (only token reference)
- Token can be used for future payments

---

### 4. Payment Authorization (Invoice - Pay with Token)

**Endpoint:** `POST https://mqtt-p100.mirillium.io/cloud-payment-vpc/api/v1/payment/authorize`

**Called From:**
- `services/mirillium/api.py` → `authorize_payment()`
- `controllers/main.py` → `payrillium_token_authorize()`
- Used when user pays invoice with saved token

**When:** User selects saved token and clicks "Pay" on invoice

**Purpose:** Authorize payment using saved token (no card data sent)

**What is Sent:**
```python
{
    "paymentInstrument": "TOKEN_REFERENCE_ONLY",  # Not card data
    "capture": True,
    "paymentType": "CARD",  # or "CHECK"
    "totalAmount": "100.00",
    "currency": "USD",
    "clientReferenceCode": "INV1234A1"
}
```

**What is Received:**
```python
{
    "success": True,
    "data": {
        "token": "transaction_id",
        "status": "AUTHORIZED",
        "amount": "100.00"
    }
}
```

**What Happens:**
- Payment is authorized using token reference
- Transaction is recorded in `payment.transaction` model
- Invoice payment status is updated

---

### 5. Payment Refund (Invoice - Refund with Token)

**Endpoint:** `POST https://mqtt-p100.mirillium.io/cloud-payment-vpc/api/v1/payment/{token}/refund`

**Called From:**
- `services/mirillium/api.py` → `refund_payment_by_token()`
- `controllers/main.py` → `payrillium_payment_refund_tokenize()`
- Used when user refunds payment from invoice

**When:** User processes refund for a payment

**Purpose:** Refund a payment using the original transaction token

**What is Sent:**
```python
{
    "totalAmount": "50.00",  # Refund amount
    "currency": "USD"
}
```

**What is Received:**
```python
{
    "success": True,
    "data": {
        "token": "refund_transaction_id",
        "status": "REFUNDED",
        "amount": "50.00",
        "receiptUrl": "https://..."
    }
}
```

**What Happens:**
- Refund is processed via Mirillium
- Refund transaction is recorded in Odoo
- Invoice credit note is created

---

### 6. Payment Link Status Update (Invoice)

**Endpoint:** `PATCH https://mqtt-p100.mirillium.io/cloud-payment-vpc/api/v1/payment/links/{link_id}`

**Called From:**
- `services/mirillium/api.py` → `patch_payment_link()`
- Used when user deactivates payment link

**When:** User deactivates or updates payment link status

**Purpose:** Update payment link status (active/inactive)

**What is Sent:**
```python
{
    "status": "INACTIVE"  # or "ACTIVE"
}
```

**What is Received:**
```python
{
    "success": True,
    "data": {
        "id": "link_id",
        "status": "INACTIVE"
    }
}
```

**What Happens:**
- Payment link status is updated in Mirillium
- Link status is synced in Odoo

---

### 7. Payment Link Notifications (Invoice - Status Check)

**Endpoint:** `GET https://mqtt-p100.mirillium.io/cloud-payment-vpc/api/v1/payment/links/{link_id}/notifications`

**Called From:**
- `services/mirillium/api.py` → `fetch_payment_link_notifications()`
- `models/account_move_get_status.py` → Cron job
- Used to check payment status for links

**When:** 
- Cron job runs every 15 minutes
- User clicks "Get Pay Status" button on invoice

**Purpose:** Fetch payment notifications for a payment link

**What is Sent:** Nothing (GET request)

**What is Received:**
```python
{
    "success": True,
    "data": {
        "payments": [
            {
                "amount": "100.00",
                "status": "PAID",
                "date": "2024-01-16"
            }
        ],
        "webhook_notifications": [...]
    }
}
```

**What Happens:**
- Payment status is checked for all active links
- Invoice payment status is updated if payment received
- Payment transactions are recorded in Odoo

---

### 8. Transaction Status Check (Invoice - ACH Status)

**Endpoint:** `GET https://mqtt-p100.mirillium.io/cloud-payment-vpc/api/v1/payment/{payment_id}/transactionStatus`

**Called From:**
- `services/mirillium/api.py` → `fetch_ach_transaction_status()`
- `models/account_move_get_status.py` → Cron job
- Used to check ACH transaction status

**When:** 
- Cron job runs every 15 minutes
- User clicks "Get Pay Status" button on invoice

**Purpose:** Check status of ACH/bank transfer transactions

**What is Sent:** Nothing (GET request)

**What is Received:**
```python
{
    "success": True,
    "data": {
        "status": "PENDING",  # or "PROCESSED", "FAILED"
        "amount": "100.00",
        "date": "2024-01-16"
    }
}
```

**What Happens:**
- ACH transaction status is checked
- Invoice payment status is updated accordingly
- Transactions are synchronized with Odoo

---

## 💻 API Calls from POS (JavaScript → Python → Mirillium Terminal)

### 9. Terminal Communication - Show Basket (POS)

**Endpoint:** `POST https://mqtt-p100.mirillium.io/cloud-payment-vpc/{terminal_serial}/local/basket`

**Called From:**
- `static/src/js/api_service.js` → `showBasket()`
- `static/src/js/product_screen.js` → `_syncBasketWithTerminal()`
- Used when products are added/removed in POS

**When:** 
- User adds product to cart
- User scans barcode
- User deletes order

**Purpose:** Send current cart/order to physical terminal to display

**What is Sent:**
```javascript
{
    "data": {
        "data": {
            "products": [
                {
                    "id": 1,
                    "name": "Product Name",
                    "qty": "2",
                    "price": "10.00",
                    "total": "20.00"
                }
            ],
            "currency": "USD",
            "subtotal": "20.00",
            "tax": "2.00",
            "discount": "0.00",
            "total": "22.00"
        }
    }
}
```

**What is Received:**
```javascript
{
    "success": true,
    "message": "Basket updated"
}
```

**What Happens:**
- Cart is displayed on physical terminal
- Terminal shows products, quantities, and total
- Customer can see order on terminal screen

---

### 10. Terminal Communication - Card Payment (POS)

**Endpoint:** `POST https://mqtt-p100.mirillium.io/cloud-payment-vpc/{terminal_serial}/local/card`

**Called From:**
- `static/src/js/api_service.js` → (via proxy)
- `controllers/main.py` → `proxy_to_terminal()` → `action="card"`
- Used when user selects Payrillium payment method in POS

**When:** User clicks "Pay" and selects Payrillium payment method

**Purpose:** Initiate card payment on physical terminal

**What is Sent:**
```javascript
{
    "data": ""  // Empty data - terminal handles card input
}
```

**What is Received:**
```javascript
{
    "success": true,
    "data": {
        "data": {
            "message": {
                "transactionId": "TXN123",
                "cardType": "CREDIT",
                "amount": "22.00",
                "entryMode": "CONTACTLESS"
            }
        }
    }
}
```

**What Happens:**
- Terminal prompts customer to insert/tap card
- Card is processed on terminal
- Payment result is returned to Odoo
- Payment transaction is recorded

---

### 11. Terminal Communication - Capture Credit (POS)

**Endpoint:** `POST https://mqtt-p100.mirillium.io/cloud-payment-vpc/{terminal_serial}/payment/auth`

**Called From:**
- `static/src/js/api_service.js` → `captureCreditPayment()`
- `controllers/main.py` → `payrillium_payment_router()` → `action="auth"`
- Used after card payment authorization

**When:** Card payment is authorized and needs capture (for credit cards)

**Purpose:** Capture authorized credit card payment

**What is Sent:**
```javascript
{
    "data": {
        "payment_id": "PAY123c",
        "amount": "22.00",
        "transaction_id": "TXN123",
        "emv_tags": "..."  // If contactless
    }
}
```

**What is Received:**
```javascript
{
    "success": true,
    "data": {
        "status": "CAPTURED"
    }
}
```

**What Happens:**
- Credit card payment is captured
- Payment transaction is finalized
- Order is marked as paid

---

### 12. Terminal Communication - Tip Selection (POS)

**Endpoint:** `POST https://mqtt-p100.mirillium.io/cloud-payment-vpc/{terminal_serial}/local/tip`

**Called From:**
- `static/src/js/api_service.js` → `showTipSelection()`
- `controllers/main.py` → `proxy_to_terminal()` → `action="tip"`
- Used when customer wants to add tip

**When:** After card payment, terminal shows tip selection

**Purpose:** Display tip selection screen on terminal

**What is Sent:**
```javascript
{
    "data": {
        "data": {
            "amount": "22.00",
            "tipOptions": ["2.00", "3.00", "5.00"]
        }
    }
}
```

**What is Received:**
```javascript
{
    "success": true,
    "data": {
        "selectedTip": "3.00",
        "total": "25.00"
    }
}
```

**What Happens:**
- Tip selection is shown on terminal
- Customer selects tip amount
- Order total is updated with tip

---

### 13. Terminal Communication - Empty Basket (POS)

**Endpoint:** `POST https://mqtt-p100.mirillium.io/cloud-payment-vpc/{terminal_serial}/local/basket`

**Called From:**
- `static/src/js/api_service.js` → `showEmptyBasket()`
- Used after payment is complete

**When:** 
- Payment is completed successfully
- Order is finalized

**Purpose:** Clear terminal display (show empty basket)

**What is Sent:**
```javascript
{
    "data": {
        "data": {
            "products": [],
            "total": "0.00"
        }
    }
}
```

**What is Received:**
```javascript
{
    "success": true
}
```

**What Happens:**
- Terminal display is cleared
- Terminal is ready for next order

---

### 14. Terminal Communication - Authorization Reversal (POS)

**Endpoint:** `POST https://mqtt-p100.mirillium.io/cloud-payment-vpc/{terminal_serial}/payment/auth_reversal`

**Called From:**
- `static/src/js/api_service.js` → `authReversal()`
- `controllers/main.py` → `payrillium_payment_router()` → `action="auth_reversal"`
- Used when payment needs to be reversed

**When:** User cancels payment or payment fails

**Purpose:** Reverse an authorized payment

**What is Sent:**
```javascript
{
    "data": {
        "payment_id": "PAY123",
        "transaction_id": "TXN123"
    }
}
```

**What is Received:**
```javascript
{
    "success": true,
    "data": {
        "status": "REVERSED"
    }
}
```

**What Happens:**
- Authorized payment is reversed
- Order is reset to unpaid state
- User can try payment again

---

### 15. Terminal Communication - Refund (POS)

**Endpoint:** `POST https://mqtt-p100.mirillium.io/cloud-payment-vpc/{terminal_serial}/payment/refund`

**Called From:**
- `static/src/js/api_service.js` → `refundDebit()` / `refundCredit()` / `refundTokenize()`
- `controllers/main.py` → `payrillium_payment_router()` → `action="refund"`
- Used when user processes refund in POS

**When:** User processes refund for a previous order

**Purpose:** Refund a payment via terminal

**What is Sent:**
```javascript
{
    "data": {
        "payment_id": "PAY123r",
        "amount": "10.00",
        "transaction_id": "TXN123",
        "cardType": "CREDIT"  // or "DEBIT"
    }
}
```

**What is Received:**
```javascript
{
    "success": true,
    "data": {
        "status": "REFUNDED",
        "refund_id": "REF123"
    }
}
```

**What Happens:**
- Refund is processed via terminal
- Refund transaction is recorded
- Order is updated with refund

---

### 16. Terminal Communication - Check Terminal Status (POS)

**Endpoint:** `POST https://mqtt-p100.mirillium.io/cloud-payment-vpc/{terminal_serial}/local/test`

**Called From:**
- `models/payrillium_terminal.py` → `_check_terminal_core()`
- `controllers/main.py` → `check_terminal_backend()`
- Used when POS session opens or user tests terminal

**When:** 
- User opens POS session
- User clicks "Check Terminal" button in terminal view

**Purpose:** Test if terminal is online and responsive

**What is Sent:**
```python
{
    "data": {}
}
```

**What is Received:**
```python
{
    "success": True,
    "data": {
        "success": True,
        "message": "Successful connection"
    }
}
```

**What Happens:**
- Terminal connectivity is verified
- Terminal status is displayed (online/offline)
- POS knows if terminal is available for payments

---

### 17. Terminal Communication - Reset Terminal (POS)

**Endpoint:** `POST https://mqtt-p100.mirillium.io/cloud-payment-vpc/{terminal_serial}/payment/abort`

**Called From:**
- `models/payrillium_terminal.py` → `_reset_terminal_core()`
- `controllers/main.py` → `reset_terminal_backend()`
- Used when user needs to reset terminal

**When:** User clicks "Reset Terminal" button

**Purpose:** Abort current terminal operation and reset state

**What is Sent:**
```python
{
    "data": {}
}
```

**What is Received:**
```python
{
    "success": True,
    "data": {
        "success": True,
        "reason": "No operation to abort"  // or operation aborted
    }
}
```

**What Happens:**
- Terminal is reset to initial state
- Any pending operations are aborted
- Terminal is ready for new operations

---

## 📋 Summary Table

| # | API Endpoint | Context | Purpose | Data Sent |
|---|-------------|---------|---------|-----------|
| 1 | `GET /api/v1/get_terminals_by_customer` | Invoice | Get available terminals | Token + Code |
| 2 | `POST /api/v1/payment/links` | Invoice | Create payment link | Invoice data |
| 3 | `POST /api/v1/tokens/payment_instrument` | Invoice | Save card token | Card data (never logged) |
| 4 | `POST /api/v1/payment/authorize` | Invoice | Authorize payment with token | Token reference only |
| 5 | `POST /api/v1/payment/{token}/refund` | Invoice | Refund payment | Amount + Currency |
| 6 | `PATCH /api/v1/payment/links/{id}` | Invoice | Update link status | Status |
| 7 | `GET /api/v1/payment/links/{id}/notifications` | Invoice | Check payment status | None (GET) |
| 8 | `GET /api/v1/payment/{id}/transactionStatus` | Invoice | Check ACH status | None (GET) |
| 9 | `POST /{serial}/local/basket` | POS | Display cart on terminal | Cart products |
| 10 | `POST /{serial}/local/card` | POS | Initiate card payment | Empty (terminal handles) |
| 11 | `POST /{serial}/payment/auth` | POS | Capture credit payment | Payment details |
| 12 | `POST /{serial}/local/tip` | POS | Show tip selection | Tip options |
| 13 | `POST /{serial}/local/basket` | POS | Clear terminal | Empty basket |
| 14 | `POST /{serial}/payment/auth_reversal` | POS | Reverse payment | Payment reference |
| 15 | `POST /{serial}/payment/refund` | POS | Process refund | Refund details |
| 16 | `POST /{serial}/local/test` | POS | Check terminal status | Empty |
| 17 | `POST /{serial}/payment/abort` | POS | Reset terminal | Empty |

---

## 🔐 Security Notes

### Data That is NEVER Sent:
- ❌ Full card numbers (only token references)
- ❌ CVV codes
- ❌ Bank account numbers (only token references)
- ❌ Customer personal information (only invoice-linked data)

### Data That is NEVER Logged:
- ❌ Card numbers
- ❌ CVV codes
- ❌ Secret keys (masked in logs)
- ❌ API tokens (masked in logs)

### Authentication:
- ✅ All requests use HMAC SHA-256 signatures
- ✅ Secret key encrypted at rest (XOR + Base64)
- ✅ Webhook signature validation
- ✅ Session and permission validation

---

## 🔄 Flow Diagrams

### Invoice Payment Flow (Token):
```
User clicks "Pay with Token"
    ↓
Select saved token
    ↓
/payrillium/token/authorize (POST)
    ↓
/api/v1/payment/authorize (Mirillium)
    ↓
Payment authorized
    ↓
Transaction recorded in Odoo
    ↓
Invoice marked as paid
```

### POS Payment Flow (Terminal):
```
User selects Payrillium payment method
    ↓
Products sent to terminal (/local/basket)
    ↓
Card payment initiated (/local/card)
    ↓
Customer inserts/taps card on terminal
    ↓
Payment authorized
    ↓
Capture payment (/payment/auth) - if credit
    ↓
Order finalized
    ↓
Empty basket sent (/local/basket)
```

### Payment Link Flow (Invoice):
```
User clicks "Generate Payment Link"
    ↓
/payrillium/generate_link (POST)
    ↓
/api/v1/payment/links (Mirillium) - Create link
    ↓
Link stored in Odoo
    ↓
Link copied to clipboard
    ↓
Customer pays via link
    ↓
Webhook received (/payment/mirillium/webhook)
    ↓
Invoice marked as paid
```

---

## 📊 Data Flow Summary

### From POS:
- **JavaScript** → **Odoo Controller** → **Mirillium Terminal API**
- All terminal operations go through Odoo controllers for security
- Terminal serial is used (not ID) for API calls

### From Invoice:
- **Odoo Backend** → **Mirillium Payment API**
- Direct API calls from Python code
- HMAC signatures for authentication

### Webhook Reception:
- **Mirillium** → **Odoo Webhook Endpoint** → **Database Update**
- HMAC signature validation required
- Invoice payment status updated automatically

---

## ✅ All Edits Explained

### Backend Changes:
1. **Security validations** - Input validation, permission checks
2. **Terminal serial handling** - Fixed to use serial instead of ID
3. **Base64 usage** - Explained for encryption, HTTP signatures, images
4. **API call routing** - Proper routing from POS/Invoice to Mirillium

### Frontend Changes:
1. **Terminal ID consistency** - Fixed to use `this.terminalId` everywhere
2. **Password field widget** - Changed to show/hide token with eye icon
3. **API service calls** - All terminal calls go through controllers

---

**All API calls are logged (with sensitive data masked) for debugging and audit purposes.**
