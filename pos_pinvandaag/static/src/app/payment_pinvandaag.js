/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { PaymentInterface } from "@point_of_sale/app/payment/payment_interface";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { markup } from "@odoo/owl";

export class PosPinVandaagPay extends PaymentInterface {
  setup() {
    super.setup(...arguments);
    this.terminal_id = null;
    this.transaction_id = null;
    this.continue_on_success = false;
    this.api = null;
    this.poller = null;
  }

  set_terminal_id(id) {
    this.terminal_id = id;
    return this;
  }

  set_transaction_id(transaction_id) {
    this.transaction_id = transaction_id;
    return this;
  }
  set_continue_on_success(continue_on_success) {
    this.continue_on_success = continue_on_success;
    return this;
  }

  set_api_type(api) {
    this.api = api;
  }

  send_payment_request(cid) {
    super.send_payment_request(cid);
    return this.__process_pinvandaag(cid);
  }

  send_payment_cancel(order, cid) {
    super.send_payment_cancel(order, cid);
    return this.cancel_request();
  }

  isJson(item) {
    item = typeof item !== "string" ? JSON.stringify(item) : item;
    try {
      item = JSON.parse(item);
    } catch (e) {
      return false;
    }
    if (typeof item === "object" && item !== null) {
      return true;
    }
    return false;
  }

  construct_pinvandaag_ticket(receipt) {
    let decodedReceipt;
    if (this.isJson(receipt)) {
      decodedReceipt = JSON.parse(receipt);
    } else {
      decodedReceipt = receipt;
    }
    if (decodedReceipt.customer) {
      decodedReceipt = decodedReceipt.customer.split("\n");
    }
    if (this.api === "Worldline") {
      return markup(
        decodedReceipt
          .map((item) => {
            if (typeof item === "string") {
              const parsed = JSON.parse(item);
              return parsed
                .map((i) => {
                  return `${i[1]}\n`;
                })
                .join(""); // Join the inner arrays
            } else {
              return `${item[1]}\n`;
            }
          })
          .join("")
          .replace(/\r/g, "")
      );
    } else {
      return markup(
        decodedReceipt
          .map((item) => {
            const parsed = JSON.parse(item);
            return parsed
              .map((i) => {
                return `${i}\n`;
              })
              .join(""); // Join the inner arrays
          })
          .join("")
          .replace(/\r/g, "")
      );
    }
  }

  async _call_pinvandaag(data) {
    return await this.env.services.orm.silent
      .call("pos.payment.method", "terminal_request", [
        [this.terminal_id],
        data,
      ])
      .catch(this._handle_odoo_connection_failure.bind(this));
  }

  async get_last_transaction_status() {
    return await this._call_pinvandaag({
      SaleToTerminal: {
        TerminalID: this.terminal_id,
        RequestType: "getLastTransaction",
      },
    });
  }

  async poll_transaction(cid) {
    const line = this.pending_pinvandaag_line();   // <-- move it here (outer scope)
    if (!line) {
      this._show_error("Payment line not found", "Pinvandaag Error");
      return false;
    }

    return await new Promise(async (resolve, reject) => {
      const Poller = async () => {
        // if payment line got removed/cancelled
        if (!line.payment_method_id) {
          line.set_payment_status("retry");
          return reject("Transaction has been cancelled");
        }

        await new Promise((r) => setTimeout(r, 1500));

        await this._call_pinvandaag({
          SaleToTerminal: {
            TerminalID: line.payment_method_id?.pinvandaag_terminal_identifier,
            RequestType: "status",
            PaymentDetails: {
              TransactionId: line.transaction_id,
            },
          },
        }).then(async (respData) => {
          switch (respData.transaction.status) {
            case "success":
              if (respData.transaction.which_api && !respData.transaction.receipt) {
                line.set_payment_status("retry");
                return reject(respData);
              }
              return resolve(respData);

            case "failed":
              line.set_payment_status("retry");
              return reject(respData);

            case "started":
            case "pending":
            case "unknown":
              this.set_transaction_id(respData.transaction.transaction_id);
              line.set_payment_status("waiting");
              return Poller();

            default:
              return Poller();
          }
        });
      };

      return Poller();
    })
      .then((respData) => {
        if (respData.transaction.status === "success") {
          this.set_api_type(respData.transaction.which_api);

          line.set_receipt_info(
            this.construct_pinvandaag_ticket(respData.transaction.receipt)
          );
          line.set_payment_status("done");
          return true;
        } else {
          line.set_payment_status("retry");
          return false;
        }
      })
      .catch((err) => {
        line.set_payment_status("retry");
        this._show_error("Transaction failed. Please try again.", "Pinvandaag Error");
        return false;
      });
  }

  pending_pinvandaag_line() {
    const line = this.pos.getPendingPaymentLine("pinvandaag");
    return line;
  }

  async __process_refund_pinvandaag(cid) {
    const line = this.pending_pinvandaag_line();

    if (!line) {
      line.set_payment_status("retry");
      this._show_error("Payment line not found");
      return;
    }

    if (line.amount == 0) {
      line.set_payment_status("retry");
      this._show_error("Select an amount above 0");
      return;
    }

    this.set_terminal_id(line.payment_method_id.pinvandaag_terminal_identifier);

    this.set_continue_on_success(
      line.payment_method_id.pinvandaag_confirm_order_on_payment
    );

    return await this._call_pinvandaag({
      SaleToTerminal: {
        TerminalID: line.payment_method_id.pinvandaag_terminal_identifier,
        PaymentDetails: {
          Amount: line.amount,
        },
        RequestType: "refund",
      },
    })
      .then(async (res) => {
        if (res.success === false)
          return this._show_error(
            res.error ||
              "Could not start transaction (refund). Contact Pin Vandaag"
          );
        if (res.status === "started" || res.status === "start") {
          line.transaction_id = res.transaction_id;
          this.transaction_id = res.transaction_id;

          return await this.poll_transaction(cid);
        }
        return false;
      })
      .catch((e) => {
        line.set_payment_status("retry");
        this._show_error(
          "Could not start transaction. Please try again.",
          "Pinvandaag Error"
        );
        return false;
      });
  }

  async __process_pinvandaag(cid) {
    const line = this.pending_pinvandaag_line();
    if (!line) {
      line.set_payment_status("retry");
      this._show_error("Payment line not found");
      return;
    }

    if (line.amount == 0) {
      line.set_payment_status("retry");
      this._show_error("Select an amount above 0");
      return;
    }
    if (line.amount < 0) {
      return await this.__process_refund_pinvandaag(cid);
    }

    this.set_continue_on_success(
      line.payment_method_id.pinvandaag_confirm_order_on_payment
    );

    return await this._call_pinvandaag({
      SaleToTerminal: {
        TerminalID: line.payment_method_id.pinvandaag_terminal_identifier,
        PaymentDetails: {
          Amount: line.amount,
        },
        RequestType: "create",
      },
    })
      .then(async (res) => {
        if (!res?.success && res.status !== "started")
          return this._show_error(
            res.error || "Could not start transaction. Contact Pin Vandaag"
          );

        line.transaction_id = res.transaction_id;
        this.transaction_id = res.transaction_id;

        return await this.poll_transaction(cid);
      })
      .catch((e) => {
        line.set_payment_status("retry");
        this._show_error(
          "Could not start transaction. Please try again.",
          "Pinvandaag Error"
        );
      });
  }
  async send_payment_cancel(order, cid) {
    super.send_payment_cancel(order, cid);
    return await this.cancel_request();
  }

  async cancel_request() {
    await this._call_pinvandaag({
      SaleToTerminal: {
        TerminalID: this.terminal_id,
        RequestType: "cancel",
        PaymentDetails: {
          TransactionId: this.transaction_id,
        },
      },
    });
  }

  _show_error(error_msg, title) {
    this.env.services.dialog.add(AlertDialog, {
      title: title || _t("Pinvandaag Error"),
      body: error_msg,
    });
  }

  _handle_odoo_connection_failure(data) {
    // handle timeout
    var line = this.pending_pinvandaag_line();
    if (line) {
      line.set_payment_status("retry");
    }
    this._show_error(
      _t(
        "Could not connect to the Odoo server, please check your internet connection and try again."
      )
    );
    return Promise.reject(data); // prevent subsequent onFullFilled's from being called
  }
}
