/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";

export class OTPInputPopup extends Component {
    static template = "Plugin_Leal.OTPInputPopup";
    static components = { Dialog };
    static defaultProps = {
        confirmText: _t("Validar"),
        cancelText: _t("Cancelar"),
        resendText: _t("Reenviar"),
        title: _t("Código OTP"),
        body: _t("Ingrese el código OTP recibido"),
    };

    setup() {
        super.setup();
        this.state = useState({
            digit1: "",
            digit2: "",
            digit3: "",
            digit4: "",
            inputValue: "",
            isResending: false,
            countdown: "00:01",
            isComplete: false
        });
        this.startCountdown();
    }

    confirm() {
        this.props.getPayload(this.state.inputValue);
        this.props.close();
    }

    getResendPayload() {
        return {
            inputValue: this.state.inputValue,
            action: 'resend'
        };
    }

    cancel() {
        this.props.getPayload(null);
        this.props.close();
    }

    async onResend() {
        this.state.isResending = true;
        const data = localStorage.getItem("_leal_redeem_data");
        const results = JSON.parse(data);
        try {
            await this.env.services.pos.data.call(
                "leal.api.settings",
                "send_otp_to_customer",
                [results],
                {}
            );

            this.env.services.notification.add(
                "Código OTP reenviado exitosamente",
                { type: 'success' }
            );
        } catch (error) {
            console.error("Error reenviando OTP:", error, results);
            this.env.services.notification.add(
                "Error al reenviar el código OTP",
                { type: 'danger' }
            );
        } finally {
            this.state.isResending = false;
        }
    }

    onInputChange(event) {
        this.state.inputValue = event.target.value;
    }

    onDigitInput(event) {
        const input = event.target;
        const index = parseInt(input.dataset.index);
        const value = input.value;

        // Solo permitir números
        if (value && !/^\d$/.test(value)) {
            input.value = '';
            return;
        }

        // Actualizar el estado del dígito correspondiente
        const digitKeys = ['digit1', 'digit2', 'digit3', 'digit4'];
        this.state[digitKeys[index]] = value;

        // Actualizar el valor completo
        this.state.inputValue = this.state.digit1 + this.state.digit2 + this.state.digit3 + this.state.digit4;

        // Verificar si está completo
        this.state.isComplete = this.state.inputValue.length === 4;

        // Mover al siguiente campo si hay un valor
        if (value && index < 3) {
            const nextInput = input.parentElement.children[index + 1];
            if (nextInput) {
                nextInput.focus();
            }
        }
    }

    onKeyDown(event) {
        const input = event.target;
        const index = parseInt(input.dataset.index);

        // Manejar retroceso
        if (event.key === 'Backspace' && !input.value && index > 0) {
            const prevInput = input.parentElement.children[index - 1];
            if (prevInput) {
                prevInput.focus();
            }
        }

        // Manejar Enter para confirmar si está completo
        if (event.key === 'Enter' && this.state.isComplete) {
            this.confirm();
        }
    }

    startCountdown() {
        let timeLeft = 60;

        const updateTimer = () => {
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            this.state.countdown = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

            if (timeLeft > 0) {
                timeLeft--;
                setTimeout(updateTimer, 1000);
            } else {
                this.state.countdown = "00:00";
            }
        };

        updateTimer();
    }
}
