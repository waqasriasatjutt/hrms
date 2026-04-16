/** @odoo-module **/

import { PaymentScreen } from '@point_of_sale/app/screens/payment_screen/payment_screen';
import { patch } from '@web/core/utils/patch';
import { setQRData, getRwCConfig } from './rwc_state';

function $(selector) {
    const elements = Array.from(document.querySelectorAll(selector));
    return {
        elements,
        // $('#id').val() / $('#id').val('foo')
        val(value) {
            if (value === undefined) {
                const el = this.elements[0];
                return el && 'value' in el ? el.value : undefined;
            } else {
                this.elements.forEach((el) => {
                    if ('value' in el) el.value = value;
                });
                return this;
            }
        },
        // $('.class').html() / $('.class').html('<b>...')
        html(value) {
            if (value === undefined) {
                const el = this.elements[0];
                return el ? el.innerHTML : undefined;
            } else {
                this.elements.forEach((el) => {
                    el.innerHTML = value;
                });
                return this;
            }
        },
    };
}

// $.ajax({...}) using fetch under the hood
$.ajax = function (options) {
    const {
        type = "GET",
        url,
        data,
        headers = {},
        success,
        error,
    } = options || {};

    const method = type.toUpperCase();
    const fetchOptions = {
        method,
        headers: headers || {},
        credentials: "same-origin",
    };

    if (method !== "GET" && data !== undefined) {
        // data is already JSON.stringify(...) in your code
        fetchOptions.body = data;
    }

    fetch(url, fetchOptions)
        .then(async (response) => {
            const text = await response.text();
            let payload = text;
            try {
                payload = JSON.parse(text);
            } catch (_) {
                // keep text if it's not valid JSON
            }

            // Simulate jQuery behavior: call error on non-2xx
            if (!response.ok) {
                if (typeof error === "function") {
                    error({
                        status: response.status,
                        responseText: text,
                        responseJSON: typeof payload === "object" ? payload : undefined,
                    });
                }
                return;
            }

            if (typeof success === "function") {
                success(payload);
            }
        })
        .catch((err) => {
            if (typeof error === "function") {
                error({
                    status: 0,
                    responseText: String(err),
                });
            }
        });
};

const jsonrpc = async (url, params = {}) => {
    const response = await fetch(url, {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({
            jsonrpc: "2.0",
            method: "call",
            params,
            id: Date.now(),
        }),
    });

    const payload = await response.json();
    if (payload.error) {
        console.error("RwC jsonrpc error", payload.error);
        throw new Error(
            (payload.error.data && payload.error.data.message) ||
            payload.error.message ||
            "JSON-RPC error"
        );
    }
    return payload.result;
};

patch(PaymentScreen.prototype, {
    async validateOrder(isForceValidate) {
        const order = this.pos.get_order();

        // Generate QR code before validating the order
        await this.generateQRCode(order);

        // Call the original validateOrder function
        super.validateOrder(isForceValidate);
    },

    async generateQRCode(order) {
        console.log("ORDER");
        console.log(getRwCConfig());
        try {
            const response = await jsonrpc('/web/dataset/call_kw', {
                model: 'rewardscodes.config',
                method: 'get_all',
                args: [],
                kwargs: {},
            });

            const data = JSON.parse(response);
            console.log("FROM RPC");
            console.log(data);
            if (!data || !data.phone || !data.mode || !data.api_key || !data.default_phone_code) {
                console.log("Rewards Codes has not been configured!");
                return;
            }

            const partner = data['phone'];
            const apiKey = data['api_key'];
            const mode = data['mode'];
            const qrEnabled = data['qr'];
            const emoneyPercent = parseFloat(data['emoney_percent'] || '1') || 0;

            if (!qrEnabled) {
                console.log("Rewards Codes QR not set");
                setQRData({disabled: true});
                return;
            }

            var quantity = 0;

            // ------------------ MODO VISIT ------------------
            if (mode === 'visit') {
                quantity = 1;

            // ------------------ MODO PRODUCT ------------------
            } else if (mode === 'product') {
                quantity = order.orderlines.reduce((sum, line) => {
                    return sum + parseFloat(line.quantity);
                }, 0);
                console.log("RwC quantity for mode=product", quantity);

            // ------------------ MODO EMONEY ------------------
            } else if (mode === 'emoney') {
                var totalWithTax = 0;

                if (order && typeof order.get_total_with_tax === 'function') {
                    totalWithTax = order.get_total_with_tax();
                } else if (order && typeof order.get_total_with_tax_incl === 'function') {
                    totalWithTax = order.get_total_with_tax_incl();
                } else if (order && 'amount_total' in order) {
                    totalWithTax = order.amount_total || 0;
                }

                console.log("RwC totalWithTax (computed)", totalWithTax);

                quantity = Math.floor((totalWithTax * emoneyPercent) / 100);
                console.log("RwC quantity for mode=emoney", quantity);

            // ------------------ MODO DESCONOCIDO ------------------
            } else {
                console.log("RwC Unknown mode, QR disabled", mode);
                setQRData({disabled: true});
                return;
            }

            // Si quantity <= 0, no generamos QR
            if (!quantity || quantity <= 0) {
                console.log("RwC Quantity is zero or invalid, QR disabled", quantity);
                setQRData({disabled: true});
                return;
            }

            const code = await getOneUseQRCode(partner, quantity, apiKey);
            // Store QR code data in the shared state
            console.log("SET QR DATA:");
            console.log("DISABLED: ", false);
            setQRData({code: code, partner: partner, disabled: false, mode: mode, quantity: quantity});
            await new Promise(resolve => setTimeout(resolve, 300));

        } catch (error) {
            setQRData({disabled: true});
            console.error("Failed to get QR code:", error);
        }
    }
});

async function getOneUseQRCode(partner, quantity, apiKey) {
    const url = `https://apig.systems:8000/rwc/get_one_use_qr_code?id=${encodeURIComponent(partner)}&quantity=${quantity}`;
    return new Promise((resolve, reject) => {
        $.ajax({
            type: "GET",
            url: url,
            headers: {
                'rwc-id': apiKey,
                'Content-Type': 'application/json'
            },
            success: function(data) {
                if (data.status === 'error') {
                    reject(data.message);
                } else {
                    resolve(data.code);
                }
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                reject(new Error(`Request failed with status: ${textStatus}`));
            }
        });
    });
}
