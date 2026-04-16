/** @odoo-module */
/* global StripeTerminal */

import { _t } from "@web/core/l10n/translation";
import { PaymentInterface } from "@point_of_sale/app/payment/payment_interface";
import { useService } from "@web/core/utils/hooks";
import { useRef } from "@odoo/owl";

import { AlertDialog, ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { makeAwaitable, ask } from "@point_of_sale/app/store/make_awaitable_dialog";
import { post } from "@web/core/network/http_service";

export class PaymentDojo extends PaymentInterface {
    setup() {
        super.setup(...arguments);
        this.webhook_resolver = null;
        this.custom_request_sent = false;
    }

    get_transaction_status(data){
        const line = this.pos.get_order().get_selected_paymentline();

        const isPopupAbsent = document.getElementsByClassName("signature_confirm_dojo")?.length === 0;
        if (isPopupAbsent && line && !this.custom_request_sent){
            line.set_payment_status("waitingDojo");
        }

        var self = this;
        var cancel_btn = document.getElementsByClassName("send_payment_cancel_dojo");
        var signature_confirm = document.getElementsByClassName("signature_confirm_dojo");
        var signature_decline = document.getElementsByClassName("signature_decline_dojo");

        if (cancel_btn[0]){
            cancel_btn[0].addEventListener("click", function () {
                self.custom_request_sent = true;
                line.set_payment_status("waiting");
                self.call_transaction_api({}, 'DELETE', data['location']);
            });
        }
        if (signature_confirm[0]){
            signature_confirm[0].addEventListener("click", function () {
                self.custom_request_sent = true;
                line.set_payment_status("waiting");
                self.call_transaction_api({"accepted": true}, 'PUT', data['location'] + '/signature');
            });
        }
        if (signature_decline[0]){
            signature_decline[0].addEventListener("click", function () {
                self.custom_request_sent = true;
                line.set_payment_status("waiting");
                self.call_transaction_api({"accepted": false}, 'PUT', data['location'] + '/signature');
            });
        }

        if (data) {
            const isSignatureVerification = data['cardholderVerificationMethod'] === "SIGNATURE";
            const hasSignatureVerificationAtFirst = data['notifications']?.[0] === "SIGNATURE_VERIFICATION";
            if (isSignatureVerification && hasSignatureVerificationAtFirst) {
                line.set_payment_status("dojoSignature");
            }
        }
        if (data && 'location' in data && !data.hasOwnProperty('transactionResult')){
            let delay = 500
            if (data['cardholderVerificationMethod'] != "SIGNATURE") {
                delay = 700
            }
            setTimeout(function() {
                self.call_transaction_api({}, 'GET', data['location']);
            }, delay)
        }
        if (data && data.hasOwnProperty('transactionResult')){
            var isPaymentSuccessful = false;
            self.update_transaction_status(data);
            var status = ["UNSUCCESSFUL","VOID", "CANCELLED"];
            if (status.includes(data['transactionResult'])){
                line.set_payment_status("retry");
                const error =  _t(data['transactionResult']);
                self._showError(error, 'Dojo Error');
            }else if (data['transactionResult'] == "DECLINED") {
                line.set_payment_status("dojoDeclined");
                const error =  _t('Transaction Declined!');
                self._showError(error, 'Declined');
            }else if (data['transactionResult'] == "SUCCESSFUL") {
                line.set_payment_status("success");
                self.update_transaction_status(data);
                self.validate_transaction(data);
                isPaymentSuccessful = true;
//                self.env.services.dialog.add(AlertDialog, {
//                    title: 'SUCCESSFUL',
//                    body: 'Transaction Successful',
//                });
            }else if (data['transactionResult'] == "TIMED_OUT"){
                line.set_payment_status('timedOut');
                const error =  _t('Transaction Timed out!');
                self._showError(error, 'Dojo Timed Out');
            }

            const resolver = this.webhook_resolver;
            if (resolver) {
                resolver(isPaymentSuccessful);
            } else {
                line.handle_payment_response(isPaymentSuccessful);
            }
        }
    }
    update_transaction_status(data){
        const transaction = {
            transactionId: data.transactionId,
            transactionTime: data.transactionTime,
            transactionType: data.transactionType,
            transactionNumber: data.transactionNumber,
            transactionResult: data.transactionResult,
            authCode: data.authCode,
            amountTotal: data.amountTotal / 100
        };
        if (transaction) {
            this.pos.get_order().set_dojo_transaction(transaction);
        }
    }
    validate_transaction(){
        const line = this.pos.get_order().get_selected_paymentline();
        this.pos.get_order().set_payment_status('success')
        line.set_payment_status("done");
    }

//    async call_transaction_api(request_data, api_request, api_url) {
//        try {
//            const data = await this.pos.data.silentCall(
//                "pos.payment.method",
//                "dojo_make_payment_request",
//                [[this.payment_method_id.id], request_data]
//            );
//            if (data?.error) {
//                throw data.error;
//            }
//        } catch (error) {
//        }
//    }

    async call_transaction_api(request_data, api_request, api_url){
        const line = this.pos.get_order().get_selected_paymentline()
        if (line){
            const config = line.payment_method_id;
            var self = this;
            const credentials = btoa(`${config.dojo_username}:${config.dojo_key}`);
            const options = {
                method: api_request,
                headers: {
                    'Authorization': `Basic ${credentials}`,
                    'Content-Type': 'application/json',
                    'Accept': 'application/connect.v2+json',
                    'Software-House-Id': self.pos.company.software_house_id,
                    'Installer-Id': config.installer_id,
                }
            };
            if (request_data && !['GET', 'HEAD'].includes(api_request.toUpperCase())) {
                options.body = JSON.stringify(request_data);
            }
            let jsonResponse;
            try {
                jsonResponse = await fetch(api_url, options);
            } catch (e) {
                console.warn(e);
                const error =  _t('Error while fetching data, please try again!');
                self._showError(error, 'Error');
                if (self.webhook_resolver) {
                    self.webhook_resolver(false);
                }
                return {};
            }

            if (!jsonResponse.ok) {
                line.set_payment_status('retry');
                if (self.webhook_resolver) {
                    self.webhook_resolver(false);
                }
                return {};
            }
            if (jsonResponse.headers.get("Content-Length") !== "0") {
                const result = await jsonResponse.json();
                self.get_transaction_status(result);
            }
            return {};
        }
//        else{
//            const resolver = this.webhook_resolver;
//            if (resolver) {
//                resolver(false);
//            }
//        }
    }
    async set_payment_terminal(data) {
        const config = this.pos.get_order().get_selected_paymentline().payment_method_id;
        const transaction_url = `${config.dojo_url}/pac/terminals/${config.terminal_id}/transactions`;
        return this.call_transaction_api(data, 'POST', transaction_url);
    }
    async send_payment_request(cid) {
        /**
         * Override
         */
        await super.send_payment_request(...arguments);
        const line = this.pos.get_order().get_selected_paymentline();
        line.set_payment_status("waitingDojo");

        if (!this.pos.company.software_house_id) {
            const error =  _t('Please Configure Software House Id in Company Configuration.');
            this._showError(error, 'Dojo Configuration');
            return false;
        }
        const terminal_amount = Math.round(line.get_amount() * 100);
        const dojo_data = {
            "transactionType": ((terminal_amount > 0) ? "SALE" : "REFUND"),
            "amount": ((terminal_amount > 0) ? terminal_amount : -terminal_amount),
            "currency": this.pos.currency.name,
        }
        const payment_intent = this.set_payment_terminal(dojo_data);
        return await new Promise((resolve) => {
            this.webhook_resolver = resolve;
        });
        return payment_intent;
    }
    async send_payment_cancel(order, cid) {
        /**
         * Override
         */
        super.send_payment_cancel(...arguments);
        const line = this.pos.get_order().get_selected_paymentline();
        line.set_payment_status("retry");
        return true;
    }
    // private methods
    _showError(msg, title) {
        if (!title) {
            title = _t("Dojo Error");
        }
        this.env.services.dialog.add(AlertDialog, {
            title: title,
            body: msg,
        });
    }
}
