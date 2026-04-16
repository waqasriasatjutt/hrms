import { _t } from "@web/core/l10n/translation";
import { PaymentInterface } from "@point_of_sale/app/payment/payment_interface";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { rpc } from "@web/core/network/rpc";
import { register_payment_method } from "@point_of_sale/app/store/pos_store";

export class PaymentGoConn extends PaymentInterface {

    setup() {
        super.setup(...arguments);
        this.most_recent_service_id = null;
    }

    async send_payment_request(cid) {
        await super.send_payment_request(cid);
        return this._go_conn_txn_create(cid);
    }

    async send_payment_cancel(order, cid) {
        await super.send_payment_cancel(order, cid);
        return this._go_conn_txn_cancel(order);
    }

    close() {
        super.close();
    }

    set_most_recent_service_id(id) {
        this.most_recent_service_id = id;
    }

    pending_go_conn_line() {
        return this.pos.getPendingPaymentLine("dtb_go_conn");
    }

    async _get_version() {
        return await rpc("/web/dataset/call_kw/ir.module.module/get_module_full_version", {
            model: 'ir.module.module',
            method: 'get_module_full_version',
            args: ['dtb_pos_go_conn_payment'],
            kwargs: {},
        });
    }

    async _go_conn_txn_create(cid) {
        const order = this.pos.get_order();
        var line = order.get_selected_paymentline();
        if (line.amount < 0) {
            this._show_error(_t('Cannot process transactions with negative amount.'));
            return false;
        }

        line.set_payment_status('waitingCard');
        const version = await this._get_version();
        this.uiLock();

        const headers = {
            "content-type": "application/json",
            "msp_program_name": "Odoo ERP, dtb_pos_go_conn_payment: " + version,
            "Access-Control-Allow-Origin": "*",
        };

        const session = order.session_id
        let db_ref_no;
        if (session && session.start_at) {
            // If start_at is a Date object, convert to string
            const startDate = session.start_at instanceof Date ? 
                session.start_at.toISOString().substring(0, 10) : 
                session.start_at.substring(0, 10);
            db_ref_no = startDate.replaceAll('-', '') + session.id;
        } else {
            // Fallback: use current date
            const currentDate = new Date().toISOString().substring(0, 10).replaceAll('-', '');
            db_ref_no = currentDate + (session ? session.id : '000');
        }
        
        const body = {
            "service_name": "doSaleTransaction",
            "service_params": {
                "db_ref_no": db_ref_no,
                "amount": line.amount.toFixed(2),
            }
        };

        try {
            const response = await fetch("http://localhost:27028", {
                method: "POST",
                headers: headers,
                body: JSON.stringify(body),
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const responseData = await response.json();
            if (responseData.status === true) {
                if (responseData.response.response_code === "000") {
                    line.set_payment_status('done');
                    const ret = responseData.response;
                    line.is_go_conn = true;
                    line.go_conn_amount = ret['amount'];
                    line.go_conn_db_ref_no = ret['db_ref_no'];
                    line.go_conn_textresponse = JSON.stringify(ret);
                    line.go_conn_resp_code = ret['response_code'];
                    line.go_conn_aid = ret['aid'];
                    line.go_conn_pan = ret['pan'];
                    line.go_conn_model = ret['model'];
                    line.go_conn_rrn = ret['rrn'];
                    line.go_conn_trace_no = ret['trace_no'];
                    line.go_conn_terminal_id = ret['terminal_id'];
                    this.uiUnLock();
                    return true;
                } else {
                    this.uiUnLock();
                    this._show_error(_t(`Код: ${responseData.response.response_code}, ${responseData.response.response_msg}`));
                    return false;
                }
            } else if (responseData.status_code === 'ng') {
                this.uiUnLock();
                this._show_error(_t(`Код: ${responseData.msg.code}, ${responseData.msg.body}`));
                return false;
            } else {
                this.uiUnLock();
                this._show_error(_t(`Код: ${responseData.response.Exception.ErrorCode}, ${responseData.response.Exception.ErrorMessage}`));
                return false;
            }
        } catch (error) {
            console.error("=error===", error);
            line.set_payment_status('retry');
            line.transaction_id = false;
            this.uiUnLock();
            this._show_error(_t(`Алдаа: ${error.message}`));
            return false;
        }
    }

    _go_conn_txn_cancel(order) {
        const line = this.pending_go_conn_line();
        line.set_payment_status('retry');
        line.transaction_id = false;
        return true;
    }

    uiLock() {
        // Remove existing event listeners
        document.removeEventListener('keypress', this.keyboard_handler);
        
        // Create overlay div
        const overlay = document.createElement('div');
        overlay.id = 'uiLockId';
        overlay.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            z-index: 1000;
            opacity: 0.6;
            width: 100%;
            height: 100%;
            color: white;
            background-color: black;
        `;
        document.body.appendChild(overlay);

        // Create message div
        const messageDiv = document.createElement('div');
        messageDiv.id = 'countdown_div';
        messageDiv.style.cssText = `
            position: absolute;
            top: 35%;
            left: 30%;
            width: 570px;
            border: 3px solid #33b5e5;
            padding: 10px;
            color: white;
            font-family: tahoma;
            font-weight: bold;
            font-size: 25px;
            z-index: 5000;
            opacity: 0.8;
            background-color: black;
        `;
        messageDiv.textContent = 'Карт унштал түр хүлээнэ үү!';
        document.body.appendChild(messageDiv);
    }

    uiUnLock() {
        const overlay = document.getElementById('uiLockId');
        const messageDiv = document.getElementById('countdown_div');
        
        if (overlay) {
            overlay.remove();
        }
        if (messageDiv) {
            messageDiv.remove();
        }
        
        // Re-add event listener
        document.addEventListener('keypress', this.keyboard_handler);
    }

    _show_error(msg, title) {
        if (!title) {
            title = _t('Go conn Error');
        }
        this.env.services.dialog.add(AlertDialog, {
            title: title,
            body: msg,
        });
    }
}

register_payment_method("dtb_go_conn", PaymentGoConn);