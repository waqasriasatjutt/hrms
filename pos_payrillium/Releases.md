version = "17-1.0.0"

### Release Summary

.

- Support for tokenized payments and refunds against tokens.
- Stored token on transaction (payrillium_card_token).
- Unified spinner (\_withSpinner).
- Token wizard fix: preserves amount on return.
- Centralized prepareRefundData: extracts reconciliationId, approvalCode, status, date.
- Signed gateway requests using prepare_signed_request()/build_header_hash() (Authorization + timestamp).

version = "17-1.0.1"

### Release Summary

- Fixed issue with created date parsing and storage.
- Implemented automatic deactivation of payment links generated for the same invoice.
- Added dynamic version display in configuration view (reads from config.py).
- Fixed payment buttons visibility: buttons now only show for posted invoices, not for draft invoices.

version = "17-1.1.1"

### Release Summary

-Added support for manual token payments (handler for manual.token.payment) with structured logging (execution_id) for auditability.
-Implemented cron_check_payment_status:
-Detects candidate invoices (active payrillium.payment.link or pending ACH transactions).
-Executes action_get_payment_status_now as SUPERUSER for each candidate invoice and aggregates results per execution_id.
-Triggers sync_existing_payment_links after cron when link payments were processed.
-Implemented action_get_payment_status_now:
-Prioritizes processing of active pay-by-link records; only checks ACH pending transactions if no link payment was processed.
-Returns a machine-friendly dict when called from cron (from_cron=True) and UI notifications when called interactively.
-Added wrapper action_get_payment_status_and_sync to combine immediate status check + conditional link sync.
-Added backend Form and List views for managing manual payments and payment links (fields: execution_id, reference, amount, state, invoice_id, terminal_id, logs; list filters and batch actions included).
-Fixed invoice_id handling and robustified payment reference generation to prevent UnboundLocalError and avoid reference collisions (uses search_count on INVLINK-{invoice.id}-{link_id} to build unique references).
-Improved logging and error handling around sync step (sync_existing_payment_links) — failures are captured and logged as sync.links events with success=false.
-Added cron-specific tests/checklist and verification steps for manual deployment/run checks.

version = "18-1.1.1"

### Release Summary

Migration notes (Odoo 17 → Odoo 18)

- Replaced tree view type with list, since tree was deprecated in Odoo 18.
- Updated Kanban views: adjusted xpath expressions because the DOM structure and classes used in pos.config kanban views changed between versions.
- Account.account no longer has the company_id field.
  delete errorpop up
  -changed name order patch

version = "18-1.1.2"

### Release Summary

- Fixed 500 Server Error when processing payments:
  - Removed 'sessionId' field from payload sent to Mirillium API (it was causing errors)
  - 'sessionId' is now only used internally in Odoo to identify the correct terminal
- Fixed terminal selection to use specific session instead of user:
  - Modified `_get_current_terminal()` to accept `session_id` parameter
  - Updated `proxy_to_terminal()` and `payrillium_payment_router()` to pass sessionId from requests
  - Now ensures each POS session sends requests to its own assigned terminal, preventing terminal confusion when multiple sessions are open
- Implemented automatic deletion of terminals that no longer exist in shopnet:
  - When synchronizing terminals, terminals not returned by shopnet API are automatically deleted from Odoo database
  - Checks for active POS sessions before deletion (skips deletion if terminal has active session)
  - Unassigns terminal from POS Config before deletion
  - Synchronization notification now shows: synchronized terminals, deleted terminals, and skipped terminals (with active sessions)
- Added terminal information logging in browser console:
  - Console logs now show which terminal (id, name, serial) each request is sent to
  - Helps with debugging and verification of correct terminal usage
