/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import {
  AlertDialog,
  ConfirmationDialog,
} from "@web/core/confirmation_dialog/confirmation_dialog";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { rpc as rpcRequest } from "@web/core/network/rpc";
import { useService } from "@web/core/utils/hooks";
import { onWillStart, onMounted } from "@odoo/owl";

import { PayrilliumAPI } from "@pos_payrillium/js/api_service";
import { loadPayrilliumConfig } from "@pos_payrillium/js/setup_config";
import {
  parseEMVData,
  generateExecutionId,
  validatePayrilliumResponse,
  updateTransactionState,
  logPayrilliumError,
} from "@pos_payrillium/js/utils";
import {
  buildPaymentReference,
  isAuthorizationSuccessful,
  getErrorMessage,
  storeTransactionMetadata,
  findRefundedOrderLine,
  prepareRefundData,
  getOriginalTransaction,
} from "@pos_payrillium/js/payment_handler";

import {
  showAmountOnTerminal,
  selectCardType,
  handleTip,
  authorizePayment,
  handleAuthorizationFailure,
  captureCredit,
  processRefund,
} from "@pos_payrillium/js/terminal_service";
import { CARD_VENDOR } from "./utils";

console.log("  POS Payrillium - Payment Screen LOADING (Odoo 17)");

patch(PaymentScreen.prototype, {
  setup(...args) {
    super.setup?.();
    this.uiService = this.env.services.ui;
    this.payrilliumAPI = PayrilliumAPI;
    this.dialog = useService("dialog");
    this.orm = useService("orm");
    this._posService = this.pos || this.env.services.pos;
    console.log("  Initializing Payrillium payment screen (Odoo 17)");
    try {
      onWillStart(async () => {
        const config = await this._loadConfiguration(this._posService);
        this._initializePaymentMethod(config);
      });

      onMounted(() => this._applyPayrilliumStyles());
    } catch (error) {
      console.error("   Configuration error:", error);
      this._showConfigurationError();
    }
  },

  async _withSpinner(fn) {
    this.uiService.block();
    try {
      return await fn();
    } finally {
      this.uiService.unblock();
    }
  },

  async _loadConfiguration(posService) {
    try {
      const config = await loadPayrilliumConfig(posService);
      console.log("config", config);
      this._applyPayrilliumStyles();
      if (!config) throw new Error("No config loaded");
      this.paymentMethodName = config.name;
      this.paymentMethodColor = config.color;
      this.paymentMethodIcon = config.icon;
      this.receivableAccountId = config.receivableAccountId;
      this.paymentProviderId = config.paymentProviderId;
      this.terminalId = config.terminalId;
      this._applyPayrilliumStyles();
      return config;
    } catch (error) {
      console.error("  Error loading configuration:", error);
    }
  },
  _applyPayrilliumStyles() {
    const buttons = [
      ...document.querySelectorAll(".paymentmethod .payment-name"),
    ];
    for (const b of buttons) {
      if (b.textContent.trim().toLowerCase() === this.paymentMethodName) {
        const button = b.closest(".paymentmethod");
        button.classList.add("payrillium-method");
        button.style.backgroundColor = this.paymentMethodColor || "#003366";
        button.style.color = "white";
        const originalIcon = button.querySelector("img:not(.payrillium-icon)");
        if (originalIcon) {
          originalIcon.remove();
        }
        let icon = button.querySelector("img.payrillium-icon");
        if (!icon) {
          icon = document.createElement("img");
          icon.className = "payrillium-icon";
          button.insertBefore(icon, button.firstChild);
        }
        icon.src =
          this.paymentMethodIcon ||
          "/pos_payrillium/static/description/icon.png";
        icon.alt = "Payrillium";
        b.style.color = "white";
        b.style.fontWeight = "bold";
      }
    }
  },

  _initializePaymentMethod(config) {
    console.log("  Configuring payment method with:", config);
    this.payrilliumAPI = PayrilliumAPI;
  },

  _showConfigurationError() {
    this.dialog.add(AlertDialog, {
      title: "Configuration error",
      body: "Could not initialize payment configuration. Check your settings.",
    });
  },

  async _createPayrilliumTransaction(params) {
    try {
      await this.orm.call(
        "payment.transaction",
        "create_from_pos_payrillium",
        [params],
        {}
      );
      console.log("  payment.transaction created for Payrillium:", params);
    } catch (error) {
      console.error("  Error creating payment.transaction:", error);
    }
  },

  /**
   * Orchestrates the full Payrillium payment process for a payment line.
   * Each step is delegated to a helper/service function for clarity and maintainability.
   * Throws an error if any step fails.
   *
   * @param {Object} paymentLine - The payment line to process.
   * @returns {Promise<boolean>} - Resolves true if payment is successful, throws otherwise.
   */
  async _processPayrilliumPayment(paymentLine, hasTerminal) {
    return await this._withSpinner(async () => {
      try {
        this.executionId = generateExecutionId();
        this.currentPaymentLine = paymentLine;
        this.transactionDataToSave = null;
        const sessionId = this._posService.session?.id || null;
        if (paymentLine.payment_token_id) {
          return await this._processPayrilliumTokenPayment(
            paymentLine,
            hasTerminal
          );
        }
        // 1. Show the payment amount and basket on the terminal
        const showAmountResult = await showAmountOnTerminal(
          this.payrilliumAPI,
          paymentLine,
          this.executionId,
          sessionId
        );
        console.log("    showAmountResult", showAmountResult);
        validatePayrilliumResponse(showAmountResult);
        const cardType = "CREDIT";
        // For testing purposes, we will use a credit card
        // 2. Request the card type selection from the terminal
        // const cardTypeResult = await selectCardType(
        //   this.payrilliumAPI,
        //    rpcRequest,
        //   this.executionId
        // );
        // console.log("    cardTypeResult", cardTypeResult);
        // validatePayrilliumResponse(cardTypeResult);
        // const cardType = cardTypeResult.data?.data?.selection;
        // 3. Handle tip selection if enabled in POS configuration
        const tipResult = await handleTip(
          this.payrilliumAPI,
          paymentLine,
          this._posService,
          this.executionId,
          sessionId
        );
        console.log("    tipResult", tipResult);
        // Check for tip cancellation
        // Validate tip response
        validatePayrilliumResponse(tipResult);
        const tipAmount = tipResult.data?.data?.tipAmount || 0;
        // 4. Authorize the payment on the terminal
        const paymentRef = buildPaymentReference();
        const paymentResult = await authorizePayment(
          this.payrilliumAPI,
          paymentLine,
          cardType,
          tipAmount,
          paymentRef,
          this.executionId,
          sessionId
        );
        console.log("    paymentResult", paymentResult);
        // Get transaction details from the response
        const message = paymentResult.data?.data?.message || {};
        const transactionId = paymentResult.data?.data?.message?.transactionId;
        this.transactionDataToSave = {
          reference: paymentRef,
          provider_id: this.paymentProviderId,
          payment_method_id: paymentLine.payment_method_id.id,
          acquirer_reference: transactionId,
          amount: parseFloat(
            paymentLine.pos_order_id.get_total_with_tax().toFixed(2)
          ),
          order_uid: paymentLine.pos_order_id.pos_reference,
          card_type: cardType,
          terminal_id: this.terminalId,
          state: "done",
        };
        console.log("    transactionDataToSave", this.transactionDataToSave);
        validatePayrilliumResponse(paymentResult);
        // 5. If the card is CREDIT, perform the capture step
        if (cardType === "CREDIT") {
          const captureResult = await captureCredit(
            this.payrilliumAPI,
            paymentLine,
            paymentRef,
            transactionId,
            this.executionId,
            message,
            sessionId
          );
          if (captureResult.data?.success === false) {
            await handleAuthorizationFailure(
              this.payrilliumAPI,
              paymentLine,
              cardType,
              captureResult,
              paymentRef,
              this.executionId,
              transactionId,
              sessionId
            );
          }
          console.log("    captureResult", captureResult);
          validatePayrilliumResponse(captureResult);
          if (this.transactionDataToSave) {
            this.transactionDataToSave.state = "done";
          }
          console.log("    transactionDataToSave", this.transactionDataToSave);
        }
        // 6. Parse EMV tags and store transaction metadata
        const parsed = message.emvTags ? parseEMVData(message.emvTags) : {};
        storeTransactionMetadata(
          this.currentOrder,
          paymentLine,
          transactionId,
          message,
          cardType,
          parsed,
          this.paymentProviderId
        );
        console.log("    transactionDataToSave", this.transactionDataToSave);
        // 7. Create the payment.transaction record in Odoo
        if (this.transactionDataToSave) {
          await this._createPayrilliumTransaction(this.transactionDataToSave);
        }
        paymentLine.transaction_id = transactionId;
        paymentLine.set_payment_status("done");
        paymentLine.provider_id = this.paymentProviderId || "";
        await this.payrilliumAPI.showEmptyBasket(this.executionId, sessionId);
        return true;
      } catch (error) {
        console.log("    errorPay", error);
        console.log("    transactionDataToSave", this.transactionDataToSave);
        if (this.transactionDataToSave) {
          this.transactionDataToSave.state = "error";
          await this._createPayrilliumTransaction(this.transactionDataToSave);
        }
        await logPayrilliumError(rpcRequest, {
          executionId: this.executionId,
          step: "error_process_payment",
          errorMessage: error?.message || "Unknown error",
          terminalId: this.terminalId,
          payload: {
            error: error?.stack || error?.toString(),
            paymentLine: {
              amount: paymentLine.amount,
              method: paymentLine.payment_method_id?.name,
            },
            transaction: this.transactionDataToSave,
          },
        });
        const formattedError = {
          payrilliumError: true,
          message: error?.message || "Payment processing error",
          originalResponse: error?.originalResponse || error?.response || error,
          cancelled: error?.cancelled || false,
          paymentLine,
        };
        paymentLine.set_payment_status("retry");
        await this._handlePaymentError(formattedError);
        return false;
      } finally {
        this.currentPaymentLine = null;
      }
    });
  },

  async _isPayrilliumPayment(paymentLine) {
    return (
      this.paymentMethodName &&
      paymentLine.payment_method_id?.name?.toLowerCase() ===
        this.paymentMethodName
    );
  },
  async validateOrder(force_validation) {
    this.executionId = generateExecutionId();
    const order = this.currentOrder;
    const total = order.get_total_with_tax();
    const lines = this.paymentLines;
    const isRefund = total < 0;
    console.log("lines", lines);

    const flags = await Promise.all(
      lines.map((l) => this._isPayrilliumPayment(l))
    );
    const hasPayrilliumPayment = flags.some(Boolean);

    if (hasPayrilliumPayment) {
      for (const line of lines) {
        console.log("line", line);
        if (!(await this._isPayrilliumPayment(line))) continue;

        try {
          if (isRefund) {
            await this._handleRefund(line, total);
          } else {
            const { hasTerminal, hasTokens } =
              await this._checkPayrilliumAvailability(order);
            console.log("hasTerminal", hasTerminal);
            console.log("hasTokens", hasTokens);
            if (!hasTerminal && !hasTokens) {
              this.dialog.add(AlertDialog, {
                title: "Payment method not available",
                body: "To use this payment method, you must either select a customer with saved cards or assign a terminal to this session.",
              });
              return false;
            }
            const proceed = await this._promptSavedCardOrContinue(
              order,
              line,
              hasTerminal
            );
            console.log("proceed", proceed);

            if (proceed) {
              if (line.payment_status !== "done" && !line.transaction_id) {
                await this._processPayrilliumPayment(line, hasTerminal);
              }
            } else {
              this.dialog.add(AlertDialog, {
                title: "Payment cancelled",
                body: "You must select a saved card or assign a terminal before proceeding with this payment.",
              });
              return false;
            }
          }
        } catch (error) {
          await this._handlePaymentError(error);
          return false;
        }
      }
    }

    return super.validateOrder(force_validation);
  },

  async _handleRefund(paymentLine, total) {
    return await this._withSpinner(async () => {
      try {
        // 1. Find the original refunded
        const executionId = generateExecutionId();
        const refundedLineBackend = await findRefundedOrderLine(
          this.currentOrder
        );
        console.log(refundedLineBackend, "refundedLineBackend");

        const order_id = refundedLineBackend?.order_id;
        if (!order_id) throw new Error("Original order not found");
        const terminalId = this.terminalId;
        // 2. Get the original transaction
        const { cardType, tokenCardId, reference, transaction_id } =
          await getOriginalTransaction(order_id);
        console.log("getOriginalTransaction:", {
          cardType,
          terminalId,
          transaction_id,
          total,
          reference,
        });
        if (!cardType || !transaction_id || !(terminalId || tokenCardId)) {
          // terminalId may be a token or id of terminal used for payment
          throw new Error("Missing required refund data");
        }
        const amount = Math.abs(total).toFixed(2);
        console.log("Starting refund process for:", {
          cardType,
          transaction_id,
          amount,
          reference,
          tokenCardId,
        });
        // 3. Process the refund
        const sessionId = this._posService.session?.id || null;
        const result = await processRefund(this.payrilliumAPI, {
          cardType: cardType.toUpperCase(),
          paymentId: reference,
          transaction_id,
          amount,
          executionId,
          tokenCardId,
          sessionId,
        });
        console.log("Refund result:", result);
        validatePayrilliumResponse(result);
        console.log("Refund validated");
        // 4. Store refund data
        const refundData = prepareRefundData(result, {
          cardType,
          transaction_id,
          terminalId,
        });
        console.log("Prepared refund data:", refundData);
        this.currentOrder.set_extra_payment_data(refundData);
        // 5. Finalize refund transaction
        await this._finalizeRefundTransaction({
          paymentLine,
          cardType,
          transaction_id,
          payment_id: `${reference}r`,
          amount,
          executionId: this.executionId,
        });
        return true;
      } catch (error) {
        console.error("Refund error:", error);
        throw error;
      }
    });
  },

  async _finalizeRefundTransaction({
    paymentLine,
    cardType,
    transaction_id,
    payment_id,
    amount,
    executionId,
  }) {
    paymentLine.transaction_id = transaction_id;
    paymentLine.set_payment_status("done");
    paymentLine.provider_id = this.paymentProviderId || "";
    console.log("paymentLine212", paymentLine);

    await this._createPayrilliumTransaction({
      reference: payment_id,
      provider_id: this.paymentProviderId,
      payment_method_id: paymentLine.payment_method_id.id,
      acquirer_reference: transaction_id,
      amount: parseFloat(amount),
      order_pos_reference: paymentLine?.pos_order_id?.pos_reference,
      card_type: cardType,
      state: "done",
      terminal_id: this.terminalId,
    });
    if (this.currentOrder?.get_due?.() === 0) {
      return super.validateOrder(false);
    }
    const sessionId = this._posService.session?.id || null;
    await this.payrilliumAPI.showEmptyBasket(executionId, sessionId);
  },

  async validatePaymentLine(paymentLine) {
    console.log("    validatePaymentLine", paymentLine);
    // You can adapt logic here if you need special validation for Payrillium
    return super.validatePaymentLine?.(paymentLine);
  },

  async _finalizeValidation() {
    const payrilliumLines = this.paymentLines.filter(
      (line) =>
        line.payment_method_id.name?.toLowerCase() === this.paymentMethodName
    );
    for (const line of payrilliumLines) {
      if (!line.transaction_id) {
        const message = `Payrillium payment without transaction ID: ${line.cid}`;
        console.error(message);
        throw new Error(message);
      }
    }
    const button = document.querySelector(".paymentmethods .selected-button");
    if (button && !button.classList.contains("payrillium-button")) {
      button.classList.add("payrillium-button");
      const icon = document.createElement("img");
      icon.src = "/pos_payrillium/static/description/icon.png";
      button.prepend(icon);
    }
    return super._finalizeValidation();
  },

  /**
   * Handles the cancellation of a payment on the terminal
   * @param {Object} event - The deletion event
   * @returns {Promise<boolean>} - True if cancellation was successful, false otherwise
   */
  async deletePaymentLine(event) {
    const paymentLine = event?.detail;
    if (!paymentLine) {
      return super.deletePaymentLine(...arguments);
    }

    if (!(await this._isPayrilliumPayment(paymentLine))) {
      return super.deletePaymentLine(...arguments);
    }

    try {
      if (paymentLine.transaction_id) {
        const executionId = generateExecutionId();
        const result = await this.payrilliumAPI.voidCapture(rpcRequest, {
          transaction_id: paymentLine.transaction_id,
          execution_id: executionId,
        });

        validatePayrilliumResponse(result);
      }

      paymentLine.set_payment_status("retry");
      return super.deletePaymentLine(...arguments);
    } catch (error) {
      this._handlePaymentError(error);
      return false;
    }
  },

  /**
   * Handles the payment request process, including terminal interaction
   * @param {Object|Event} lineOrEvent - Payment line object or event containing payment details
   * @returns {Promise<boolean>} - True if payment was successful, false otherwise
   */
  async sendPaymentRequest(line) {
    console.log("sendPaymentRequest", line);
    console.log("this.paymentMethodName", this.paymentMethodName.toLowerCase());

    const methodName = line.payment_method_id?.name?.toLowerCase();
    console.log("methodName", methodName);

    const isOurMethod =
      this.paymentMethodName &&
      methodName === this.paymentMethodName.toLowerCase();

    console.log("isOurMethod", isOurMethod);

    if (!isOurMethod) {
      if (super.sendPaymentRequest) {
        return super.sendPaymentRequest(line);
      }
      return super.send_payment_request?.(line);
    }

    if (line.payment_status === "done" || line.transaction_id) {
      if (this.currentOrder?.get_due?.() === 0) {
        return super.validateOrder?.(false);
      }
      return true;
    }

    const order = this.currentOrder;

    console.log(order, "order");

    order.select_paymentline(line);
    const { hasTerminal, hasTokens } = await this._checkPayrilliumAvailability(
      order
    );
    if (!hasTerminal && !hasTokens) {
      this.dialog.add(AlertDialog, {
        title: "Payment method not available",
        body: "To use this payment method, you must either select a customer with saved cards or assign a terminal to this session.",
      });
      if (order?.remove_paymentline) order.remove_paymentline(line);

      return false;
    }

    try {
      const total = order.get_total_with_tax();
      const isRefund = total < 0;

      if (isRefund) {
        await this._handleRefund(line, total);
      }

      if (line.payment_status === "retry" && !line.transaction_id) {
        await this._processPayrilliumPayment(line, hasTerminal);
        if (order?.get_due?.() === 0) {
          return super.validateOrder?.(false);
        }
        return true;
      }
    } catch (error) {
      console.error("Payment processing error:", error);
      await this._handlePaymentError(error);
      return false;
    }
  },

  async _handlePaymentError(error) {
    console.error("Payment error details:", error);

    // Ensure we have a structured error object
    const errorObj = typeof error === "string" ? { message: error } : error;

    // Log the full response for debugging
    if (errorObj.originalResponse) {
      console.log("Original terminal response:", errorObj.originalResponse);
    }

    // Get the most specific error message available
    const errorMessage =
      errorObj.originalResponse?.data?.data?.message || // From terminal response
      errorObj.message || // From error object
      "An unexpected error occurred";

    // Set payment line status to retry if we have a payment line
    const paymentLine = errorObj.paymentLine || this.currentPaymentLine;
    if (paymentLine) {
      paymentLine.set_payment_status("retry");
    }

    // Show popup using the same format as other Odoo modules
    this.dialog.add(AlertDialog, {
      title: errorObj.cancelled ? "Cancelled operation" : "Payment error",
      body: errorMessage,
    });
  },

  async _checkPayrilliumAvailability(order) {
    const terminal = this._posService.config.payrillium_terminal_serial;
    console.log("terminal", terminal);
    const partner = order.get_partner();

    const isString = typeof terminal === "string";
    console.log("isString", isString);

    const hasTerminal = terminal && isString && terminal.length > 0;
    if (hasTerminal) {
      console.log("  Terminal assigned to session.");
    }

    if (!partner || !partner.id) {
      console.warn("  No customer selected, and  terminal assigned.");
      return { hasTerminal, hasTokens: false };
    }

    const tokens = await this.orm.call(
      "payment.token",
      "search_read",
      [
        [
          ["partner_id", "=", partner.id],
          ["active", "=", true],
          ["provider_id.code", "=", "payrillium"],
        ],
        ["id"],
      ],
      {}
    );

    const hasTokens = tokens.length > 0;
    if (!hasTokens) {
      console.warn("  Customer selected but has no active tokens.");
    }

    return { hasTerminal, hasTokens };
  },

  async _promptSavedCardOrContinue(order, paymentLine, hasTerminal) {
    console.log("  Checking for saved cards for customer...");

    const partner = order.get_partner();
    if (!partner || !partner.id) {
      console.log(" No customer assigned to order, skipping token check.");
      return true;
    }

    try {
      console.log("  Fetching active tokens for partner ID:", partner.id);

      // Primero probemos sin filtros para ver todos los tokens
      const allTokens = await this.orm.call(
        "payment.token",
        "search_read",
        [
          [["partner_id", "=", partner.id]],
          [
            "id",
            "payment_details",
            "provider_ref",
            "token_type",
            "active",
            "provider_id",
          ],
        ],
        {}
      );
      console.log("  ALL tokens for partner (no filters):", allTokens);

      const activeTokens = await this.orm.call(
        "payment.token",
        "search_read",
        [
          [
            ["partner_id", "=", partner.id],
            ["active", "=", true],
          ],
          [
            "id",
            "payment_details",
            "provider_ref",
            "token_type",
            "provider_id",
          ],
        ],
        {}
      );
      console.log("  ACTIVE tokens for partner:", activeTokens);

      // Ahora con filtro de provider
      const payrilliumTokens = await this.orm.call(
        "payment.token",
        "search_read",
        [
          [
            ["partner_id", "=", partner.id],
            ["active", "=", true],
            ["provider_id.code", "=", "payrillium"],
          ],
          ["id", "payment_details", "provider_ref", "token_type"],
        ],
        {}
      );
      console.log("  PAYRILLIUM tokens for partner:", payrilliumTokens);

      const cardTokens = await this.orm.call(
        "payment.token",
        "search_read",
        [
          [
            ["partner_id", "=", partner.id],
            ["active", "=", true],
            ["token_type", "=", "card_payment"],
          ],
          [
            "id",
            "payment_details",
            "provider_ref",
            "token_type",
            "provider_id",
          ],
        ],
        {}
      );
      console.log("  CARD_PAYMENT tokens for partner:", cardTokens);

      const tokens = payrilliumTokens;

      console.log(`  ${tokens.length} token(s) found.`);
      console.log("  Tokens data:", tokens);

      if (!tokens.length) {
        console.log("  No saved cards found for this customer.");
        return true;
      }

      // Map tokens to selection list format
      const tokenList = tokens.map((token) => {
        const label =
          token.payment_details || `****${token.provider_ref.slice(-4)}`;
        console.log(`  Token ${token.id}: ${label}`);
        return {
          id: token.id,
          label: label,
          isSelected: false,
          item: token,
        };
      });

      const simpleTokenList = tokens.map((token) => ({
        id: token.id,
        text: token.payment_details || `****${token.provider_ref.slice(-4)}`,
        value: token.id,
      }));

      console.log("  Simple token list:", simpleTokenList);

      console.log("  Token list for dialog:", tokenList);
      console.log("  About to call makeAwaitable() with:", {
        title: "Select a saved card",
        list: tokenList,
      });

      const selectedToken = await makeAwaitable(this.dialog, SelectionPopup, {
        title: "Select a saved card",
        list: tokenList,
      });

      console.log("  makeAwaitable() returned:", selectedToken);
      console.log("  selectedToken type:", typeof selectedToken);
      console.log("  selectedToken value:", selectedToken);

      if (selectedToken) {
        console.log("  Token selected:", selectedToken);
        paymentLine.payment_token_id = selectedToken;
        return true;
      } else {
        console.log("  No token selected or user cancelled");
        if (!hasTerminal) {
          console.log("  No terminal and user cancelled token selection.");
          return false;
        }
        console.log("  User chose not to use a saved token.");
        return true;
      }
    } catch (err) {
      console.warn("   Error retrieving or selecting saved cards:", err);
      return true;
    }
  },

  async _processPayrilliumTokenPayment(paymentLine, hasTerminal) {
    return await this._withSpinner(async () => {
      console.log("  Starting token-based payment flow");

      try {
        console.log("  paymentLine:", paymentLine);
        console.log("  paymentLine.order:", paymentLine.order);
        console.log("  this.currentOrder:", this.currentOrder);

        const order = paymentLine.order || this.currentOrder;
        const token = paymentLine.payment_token_id;

        if (!token || !token.id || !token.provider_ref) {
          console.error("  Invalid token object in payment line:", token);
          throw new Error("Invalid payment token");
        }

        if (!order) {
          console.error("  No order found in paymentLine or currentOrder");
          throw new Error("No order found");
        }

        const amount = order.get_total_with_tax();
        const currency = "USD";

        console.log(
          "  Sending backend request to /payrillium/token/authorize",
          {
            token_id: token.id,
            amount,
            currency,
            provider_id: this.paymentProviderId,
          }
        );

        const result = await rpcRequest("/payrillium/token/authorize", {
          token_id: token.id,
          amount,
          currency,
          provider_id: this.paymentProviderId,
        });

        console.log("result", result);

        if (!result.success) {
          console.error("  Authorization failed:", result.message);
          throw new Error(result.message || "Authorization failed");
        }
        validatePayrilliumResponse(result.authorization_data);

        const data = result.authorization_data.data || {};

        const transactionId = data.token || "N/A";
        const clientRef = data.token || data.metadata?.id;
        if (!clientRef) {
          throw new Error(result.message || "Authorization failed");
        }
        console.log("  Authorization succeeded:", {
          transactionId,
          clientRef,
        });

        const metadata = result.authorization_data?.data?.metadata || {};
        const processor = metadata.processorInformation || {};
        const paymentInfo = metadata.paymentInformation || {};
        const tokenCard = paymentInfo.tokenizedCard || {};
        const formattedDate = (
          metadata.submitTimeUtc || new Date().toISOString()
        )
          .replace("T", " ")
          .replace("Z", "");

        const messageForReceipt = {
          approvalCode: processor.approvalCode || "N/A",
          cardVendor: CARD_VENDOR[tokenCard.type] || "N/A",
          cardNumber: "****",
          transactionId: processor.transactionId || transactionId || "N/A",
          terminalId: "N/A",
          entryMode: "TOKEN",
          date: formattedDate,
          status: metadata.status || "AUTHORIZED",
          rawBody: metadata,
        };
        const parsedEMV = {};
        storeTransactionMetadata(
          order,
          paymentLine,
          transactionId,
          messageForReceipt,
          "card_payment",
          parsedEMV,
          this.paymentProviderId
        );

        this.transactionDataToSave = {
          reference: clientRef,
          provider_id: this.paymentProviderId,
          payment_method_id: paymentLine.payment_method_id.id,
          acquirer_reference: transactionId,
          amount: parseFloat(amount.toFixed(2)),
          order_uid: order.uid,
          card_type: "card_payment",
          state: "done",
          payrillium_card_token: token.provider_ref,
        };

        console.log("  transactionDataToSave:", this.transactionDataToSave);
        paymentLine.transaction_id = transactionId;
        paymentLine.set_payment_status("done");
        await this._createPayrilliumTransaction(this.transactionDataToSave);

        if (hasTerminal) {
          const sessionId = this._posService.session?.id || null;
          await this.payrilliumAPI.showEmptyBasket(this.executionId, sessionId);
        }
        console.log("  Payment transaction created successfully.");
        return true;
      } catch (error) {
        console.error("  Error processing token payment:", error);
        throw error;
      }
    });
  },
});

console.log("  POS Payrillium - Payment Screen READY (Odoo 17)");
