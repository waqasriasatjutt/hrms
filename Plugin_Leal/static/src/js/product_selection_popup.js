/** @odoo-module **/

import { Component, useState, reactive, onWillUnmount } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";
import { OTPInputPopup } from "./otp_input_popup";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";

export class ProductSelectionPopup extends Component {
    static template = "Plugin_Leal.ProductSelectionPopup";
    static components = { Dialog };
    static defaultProps = {
        confirmText: _t("Seleccionar"),
        cancelText: _t("Cancelar"),
        title: _t("Seleccionar producto"),
        body: _t("Seleccione un producto de la lista:"),
        products: [],
        customer_uid: null,
    };

    setup() {
        super.setup();
        this.pos = usePos();
        this.dialog = useService("dialog");
        this.state = useState({
            selectedProduct: null,
            hasOtp: false,
            commerceData: null,
            askForOtpData: null,
            totalLealRewardPoints: 0,
            lealRedeemData: localStorage.getItem('leal_redeem_data') ? JSON.parse(localStorage.getItem('leal_redeem_data')) : []
        });
        this.lastDocumentNumber = null;
        this.getCommerceHasOtp();
    }

    async getCommerceHasOtp() {
        const result = await this.pos.data.call(
            "leal.user.data",
            "search_read",
            [[], ['tiene_otp']],
            {}
        );
        this.state.hasOtp = result[0].tiene_otp;
    }

    cancel() {
        this.props.close();
    }

    getPayload() {
        return {
            selectedProduct: this.state.selectedProduct,
        };
    }

    // Método para guardar el documento en memoria
    setLastDocumentNumber(documentNumber) {
        this.lastDocumentNumber = documentNumber;
    }

    // Método para obtener el documento guardado
    getLastDocumentNumber() {
        return this.lastDocumentNumber;
    }

    // Method to find POS product by Leal product code
    getPosProduct(lealProduct) {
        const posProduct = this.pos.models['product.product'].find(p => p.default_code === lealProduct.codigo_premio || p.barcode === lealProduct.codigo_premio);
        return posProduct;
    }

    // Method to get product image URL
    getProductImageUrl(lealProduct) {
        const posProduct = this.getPosProduct(lealProduct);
        if (posProduct && posProduct.id) {
            return `/web/image?model=product.template&field=image_128&id=${posProduct.id}&unique=${posProduct.write_date}`
        }
        return "/Plugin_Leal/static/img/product-placeholder.svg";
    }

    // Method to check if we should show POS image or placeholder
    shouldShowPosImage(lealProduct) {
        const posProduct = this.getPosProduct(lealProduct);
        return posProduct && posProduct.id;
    }

    // Method to check if product is available (has POS match)
    isProductAvailable(lealProduct) {
        const posProduct = this.getPosProduct(lealProduct);
        return posProduct && posProduct.id;
    }

    // Method to check if product should be clickable
    isProductClickable(lealProduct) {
        return this.isProductAvailable(lealProduct);
    }

    async onSelectProduct(product, user_uid) {
        this.state.selectedProduct = product;
        const posProduct = this.getPosProduct(product);
        this.props.close();
        // 1. Enviar OTP al cliente
        if (this.state.hasOtp) {
            this.env.services.ui.block();
            this.state.commerceData = await this.pos.data.call(
                "leal.user.data",
                "search_read",
                [[["id_comercio", "=", this.state.selectedProduct.id_comercio], ["activo", "=", true]], ['uid_cms', 'id_comercio', 'nombre_comercio', 'id_sucursal', 'tiene_otp']],
                {}
            );
            this.state.askForOtpData = {
                id_comercio: product.id_comercio,
                id_externo: String(this.pos.config.id),
                uid_cms: this.state.commerceData[0].uid_cms,
                uid: user_uid,
                id_premio: product.id_premio,
                codigo_premio: product.codigo_premio,
            };
            const otpResult = await this.pos.data.call(
                "leal.api.settings",
                "send_otp_to_customer",
                [this.state.askForOtpData],
                {}
            );
            localStorage.setItem("_leal_redeem_data", JSON.stringify(this.state.askForOtpData));
            if (parseInt(otpResult.code) !== 100) {
                this.env.services.ui.unblock();
                this.env.services.notification.add(
                    'Error al enviar OTP al cliente, inténtelo de nuevo',
                    { type: 'danger' }
                );
                localStorage.removeItem("_leal_redeem_data");
                return;
            }
            // 2. Abrir modal para ingresar el OTP
            this.env.services.ui.unblock();
            const responseOtp = await makeAwaitable(this.dialog, OTPInputPopup, {
                title: _t("Ingresa código de validación"),
                body: _t("Confirma la redención con el código OTP"),
                confirmText: _t("Validár código"),
                resendText: _t("Reenviar"),
                cancelText: _t("Cancelar"),
            });

            if (responseOtp && responseOtp.length === 4) {
                this.env.services.ui.unblock();
                const orderlines = this.pos.get_order().get_orderlines();
                const existsReward = orderlines.find((orderline) => {
                    return orderline.product_id.default_code === this.state.selectedProduct.codigo_premio;
                });
                // Si el producto ya existe en la orden, actualizar la cantidad
                // Solo si el comertcio no tiene OTP
                if (existsReward && existsReward.id && !this.state.hasOtp) {
                    existsReward.set_quantity(existsReward.get_quantity() + 1);
                    this.state.totalLealRewardPoints = existsReward.get_quantity() * this.state.selectedProduct.puntos;
                }
                else {
                    this.state.totalLealRewardPoints = this.state.totalLealRewardPoints + this.state.selectedProduct.puntos;
                    this.addProductToOrder(posProduct, user_uid, responseOtp);
                }
            }
        }
        else {
            this.state.totalLealRewardPoints = this.state.totalLealRewardPoints + this.state.selectedProduct.puntos;
            this.addProductToOrder(posProduct, user_uid, null);
        }

        return true;
    }

    async addProductToOrder(posProduct, user_uid, otp_value) {
        try {
            const order = this.pos.get_order();
            await reactive(this.pos).addLineToCurrentOrder({ product_id: posProduct.id });
            const selectedLine = order.get_selected_orderline();
            if (selectedLine) {
                selectedLine.set_unit_price(0);
                selectedLine.set_discount(100);
                const lealRedemptionData = {
                    "odoo_id": selectedLine.id,
                    "odoo_order_uuid": order.uuid,
                    "id_comercio": this.state.selectedProduct.id_comercio,
                    "id_sucursal": null,
                    "uid_customer": user_uid,
                    "id_premio": this.state.selectedProduct.id_premio,
                    "codigo_premio": this.state.selectedProduct.codigo_premio,
                    "otp_value": otp_value,
                    "redimido": false,
                };
                selectedLine.set_leal_redeem_data(lealRedemptionData);
                // selectedLine.setNote(JSON.stringify(lealRedemptionData));
                this.state.lealRedeemData.push(lealRedemptionData);
                localStorage.setItem('leal_redeem_data', JSON.stringify(this.state.lealRedeemData));
            }
            // Notificación eliminada aquí para evitar duplicados
        } catch (error) {
            console.error("Error al agregar el producto a la orden:", error);
            this.env.services.notification.add(
                'Error al agregar el producto a la orden',
                { type: 'danger' }
            );
        }
    }
}