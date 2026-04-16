/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { PaymentInterface } from "@point_of_sale/app/payment/payment_interface";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { register_payment_method } from "@point_of_sale/app/store/pos_store";
import { QRPopup } from "@point_of_sale/app/utils/qr_code_popup/qr_code_popup";
import { ask } from "@point_of_sale/app/store/make_awaitable_dialog";
import { DigiPayQrPopup } from "@kb_pos_digi_pay/app/digi_qr_popup";

// Delay function replacement for web.concurrency
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

export class PaymentDigiPay extends PaymentInterface {

    setup() {
        super.setup(...arguments);
        this.most_recent_service_id = null;
        this.currentPopup = null;
    }

    async send_payment_request(cid) {
        await super.send_payment_request(cid);
        return this._digipay_invoice_create(cid);
    }

    async send_payment_cancel(order, cid) {
        await super.send_payment_cancel(order, cid);
        return this._digipay_invoice_cancel(order);
    }

    close() {
        super.close();
    }

    set_most_recent_service_id(id) {
        this.most_recent_service_id = id;
    }

    pending_digipay_line() {
        return this.pos.getPendingPaymentLine("digi_pay");
    }

    set_most_recent_service_id(id) {
        this.most_recent_service_id = id;
    }

    set_invoice_id(invoice_id) {
        this.invoice_id = invoice_id;
    }

    get_invoice_id() {
        return this.invoice_id;
    }

    // ========================== CUSTOM methods ===========********************************************

    async _digipay_invoice_create(cid) {
        const order = this.pos.get_order();
        var self = this;

        var line = order.get_selected_paymentline();
        if (line.amount < 0) {
            this._show_error(_t('Cannot process transactions with negative amount.'));
            return false;
        }
        const session = order.session_id
        console.log("====_digipay_invoice_create", line, session, order);
        var amount = line.amount;
        line.set_payment_status('waitingCard');
        // =======================================================

        self.env.services.orm.call('digi.pay.integration', 'create_invoice', [
            order.name, order.config.id, amount, session.id
        ]).then(function(result){
            if (result) {
                if(result['status'] === 'ok'){
                    console.log("==result", result);
                    self.set_invoice_id(result['invoice_id']);
                    line.transaction_id = result['invoice_id'];
                    line.qr_data = result['qr_data'];
                    const qrCode = "data:image/png;base64," + result['qr_data'];
                    // Store popup reference and payment done flag
                    self.currentPopup = ask(
                        self.env.services.dialog,
                        {
                            title: _t('DigiPay QR'),
                            qrCode: qrCode,
                            amount: line.amount,
                            // Confirm button-ийг нуух - confirmLabel-ийг undefined болгох
                            confirmLabel: "Төлбөр шалгах",
                            confirm: () => {
                                self.checkInv(order);
                            },
                            cancelLabel: "Цуцлах",
                            // cancelInv function-ийг onCancel prop-оор дамжуулах
                            onCancel: () => {
                                self.cancelInv();
                            },
                            onDismiss: () => {
                                self.cancelInv();
                            },
                        },
                        {},
                        DigiPayQrPopup
                    );
                    self.checkInv(order);
                    // console.log("====================currentPopup:", self.currentPopup);
                    // // Handle popup close - QRPopup нь confirm/cancel хийхэд promise resolve/reject хийх
                    // self.currentPopup.then(function(result) {
                    //     console.log("====================popup then result:", result);
                    //     if (result === false) {
                    //         self.cancelInv();
                    //         self.currentPopup = null;
                    //     }
                    // }).catch(function(error) {
                    //     console.log("====================popup catch error:", error);
                    //     self.cancelInv();
                    //     self.currentPopup = null;
                    // });
                } else {
                    self._show_error(_t('Message from DigiPay: %s, (%s)').replace('%s', result['body']).replace('%s', result['code']));
                    return Promise.resolve();
                }
            }
        });
    }

    async _digipay_invoice_cancel(order) {
        var self = this;
        var line = order.get_selected_paymentline();
        var invoice_id = self.get_invoice_id();
        console.log("=invoice_id", invoice_id, line);

        line.set_payment_status('retry');
        line.transaction_id = false;
        self.set_invoice_id(null);
    }

    cancelInv(){
        console.log("===cancelInv clicked!", invoice_id);
        var self = this;
        var invoice_id = self.get_invoice_id();
        var self = this;
        const order = this.pos.get_order();
        if (invoice_id) {
            self.env.services.orm.call('digi.pay.integration', 'cancel_invoice', [
                order.config.id, invoice_id
            ]).then(function(result){
                self._digipay_invoice_cancel(self.pos.get_order());
            });
        }
    }

    checkInv(order) {
        var self = this;
        var invoice_id = self.get_invoice_id();
        if (invoice_id) {
            console.log("===checkInv clicked!", invoice_id);
            const order = this.pos.get_order();
            self.env.services.orm.call('digi.pay.integration', 'check_invoice', [
                order.config.id, invoice_id
            ]).then(function(result){
                console.log('check result', result);
                if (result['status'] == 'paid') {
                    // To paid
                    var line = order.get_selected_paymentline();
                    if(line){
                        // Save data
                        var ret = result['ret'];
                        line.is_digipay = true;
                        line.digipay_status = result['status'];
                        line.digipay_db_ref_no = ret['db_ref_no'];
                        line.digipay_textresponse = JSON.stringify(ret);;
                        line.digipay_resp_code = ret['resp_code'];
                        line.digipay_terminal_id = ret['extra_data']['terminal_id'];
                        line.digipay_approval_code = ret['extra_data']['approval_code'];
                        line.digipay_payment_request_id = ret['extra_data']['payment_request_id'];
                        line.digipay_rrn = ret['extra_data']['rrn'];
                        line.set_payment_status('done');
                        // Popup-ийг confirm хийж хаах
                        setTimeout(function() {
                            self.env.services.dialog.closeAll();
                        }, 100);
                        return true;
                    }
                } else if (result['status'] == 'pending') {
                    return delay(1500)
                        .then(function() {
                            self.checkInv(order);
                        });
                } else if (result['status'] == 'expired') {
                    console.log("=expired==", result['status']);
                    // Popup-ийг хаах - dialog service-ийн closeAll() method ашиглах
                    self.env.services.dialog.closeAll();
                    return false;
                }
                else {
                    console.log("=???????==", result['status']);
                    return false;
                }
            });
        }
    }

    // *************************************************************************************************
    _show_error(msg, title) {
        if (!title) {
            title = _t('DigiPay Error');
        }
        this.env.services.dialog.add(AlertDialog, {
            title: title,
            body: msg,
        });
    }
}

register_payment_method("digi_pay", PaymentDigiPay);
