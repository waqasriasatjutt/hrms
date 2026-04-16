/** @odoo-module **/

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { OTPInputPopup } from "./otp_input_popup";
import { _t } from "@web/core/l10n/translation";
import { isRefund, refundAction, validateToken, validateCustomer, calculateAuthValue, validateIfExistsOTP, updateProductsToCampaign } from "./payment_utils";
// import { validateToken, validateCustomer, calculateAuthValue, validateIfExistsOTP, renewOtp } from "./payment_utils";
import { onWillStart, useState, onMounted, reactive, onWillUnmount } from "@odoo/owl";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { redeemCampaign } from "./campaign_redeem_utils";


patch(PaymentScreen.prototype, {
    async setup() {
        super.setup();
        this.dialog = useService("dialog");
        this.state = useState({
            redencion_abierta: 0,
            hideLealPayment: false,
            commerceData: null,
            redeemResponse: null,
            data_redencion: null,
            lealRedeemData: localStorage.getItem('leal_redeem_data') ? JSON.parse(localStorage.getItem('leal_redeem_data')) : [],
            hasLealProducts: false,
            hasAccumulatePoints: false,
        });

        // this.payment_methods_from_config = this.removeLealPaymentMethod()

        onWillStart(async () => {
            this.payment_methods_from_config = await this.removeLealPaymentMethod();
            await this.validateCampaignsOnLoad();
        });

        onMounted(() => {
            const payments = document.getElementsByClassName("paymentmethod");
            for (const pay of payments) {
                const name = pay.children[0].children[1].innerText.toLowerCase();
                if (name.includes('leal')) {
                    pay.classList.add('leal-yellow-bg');
                }
            }
        });

        onWillUnmount(() => {
            localStorage.removeItem("leal_campaign_redeem_data");
        });
    },

    async removeLealPaymentMethod() {
        const allPaymentMethods = this.pos.config.payment_method_ids;
        const result = await this.pos.data.call(
            "leal.user.config",
            "search_read",
            [[["config_key", "=", "redencion_abierta"]], ["config_value_int"], 0, 1]
        );

        this.state.redencion_abierta = result[0].config_value_int || 0;


        const config = result && result[0];
        if (config && config.config_value_int === 0) {
            this.state.hideLealPayment = true;
        }

        // Si hideLealPayment está activo, excluir el método de pago 'Leal'
        if (this.state.hideLealPayment) {
            const filteredMethods = allPaymentMethods.filter(method => {
                const methodName = method.name.toLowerCase();
                return !methodName.includes('leal') && !method.journal?.code?.toLowerCase().includes('leal');
            });
            return filteredMethods;
        }
        return allPaymentMethods;

    },

    // Sobrescribir el método validateOrder para incluir lógica de redención Leal
    async validateOrder(isForceValidate) {
        this.env.services.ui.block();
        const order = this.pos.get_order();
        const orderlines = order.get_orderlines();

        //Lógica para la anulación Leal
        if (isRefund(order)) {
            const response = await refundAction(order, this.env, this.pos);
            if (response) super.validateOrder(isForceValidate);
            return;
        }

        // Acumulación de puntos
        if (this.state.hasAccumulatePoints) {
            const responseRedeemCampaigns = await this.accumulatePoints(order);
            if (!responseRedeemCampaigns) {
                this.dialog.add(ConfirmationDialog, {
                    title: _t("Error"),
                    body: _t("No se pudo redimir las campañas. Por favor, intente de nuevo."),
                });
                this.env.services.ui.unblock();
                return;
            }
        }

        this.state.hasLealProducts = this.state.lealRedeemData && this.state.lealRedeemData.length > 0;

        if (this.state.hasLealProducts) {
            const orderTotal = order.get_total_with_tax();
            if (orderTotal === 0) {
                const allow_zero_invoices = await this.pos.data.call(
                    "leal.api.settings",
                    "search_read",
                    [[["active", "=", "true"]], ["allow_zero_invoices"], 0, 1]
                );
                if (allow_zero_invoices && allow_zero_invoices.length > 0) {
                    if (!allow_zero_invoices[0].allow_zero_invoices) {
                        this.env.services.notification.add(
                            "No se pueden crear facturas en $0 para productos Leal. Configure esta opción en Configuración → Técnico → Leal API settings.",
                            { type: 'danger' }
                        );
                        this.env.services.ui.unblock();
                        return;
                    }
                }
            }

            try {
                const commerce = await this.pos.data.call(
                    "leal.user.data",
                    "search_read",
                    [[['activo', '=', true]], ['uid_cms', 'id_comercio', 'nombre_comercio', 'id_sucursal', 'tiene_otp'], 0, 1],
                );
                this.state.commerceData = commerce[0] || null;
            } catch (error) {
                this.env.services.notification.add(
                    "No se pudo obtener la información del comercio para la redención Leal",
                    { type: 'warning' }
                );
            }

            for (const product of this.state.lealRedeemData) {
                if (product.redimido) {
                    continue;
                }
                let otp_value = product.otp_value;
                if (this.state.commerceData?.tiene_otp && !otp_value) {
                    this.env.services.notification.add(
                        "Código OTP requerido para completar la redención Leal",
                        { type: 'warning' }
                    );
                    this.env.services.ui.unblock();
                    return;
                }
                let data_redencion = null;

                //Validación si el comercio tiene OTP activo
                if (product.codigo_premio === 'DISC_LEAL') {
                    data_redencion = {
                        "id_comercio": this.state.commerceData.id_comercio,
                        "id_externo": String(this.pos.config.id),
                        "uid": product.uid_customer,
                        "factura": `${order.name}_${Date.now()}` || "POS-" + Date.now(),
                        "valor": product.id_premio,
                    };
                    if (this.state.commerceData?.tiene_otp) {
                        data_redencion.OTP = otp_value;
                    }
                }
                else {
                    data_redencion = {
                        "id_comercio": this.state.commerceData.id_comercio,
                        "id_externo": String(this.pos.config.id),
                        "uid": product.uid_customer,
                        "factura": `${order.name}_${Date.now()}` || "POS-" + Date.now(),
                        "id_premio": product.id_premio,
                    };
                    if (this.state.commerceData?.tiene_otp) {
                        data_redencion.OTP = otp_value;
                    }
                }
                try {
                    const redeemResponse = await this.pos.data.call(
                        "leal.api.settings",
                        "redeem_points",
                        [data_redencion],
                    );
                    this.state.redeemResponse = redeemResponse;
                } catch (error) {
                    this.state.redeemResponse = {
                        code: 999,
                        message: "Error al comunicarse con el servidor de redención: " + (error.message || error)
                    };

                    this.env.services.notification.add(
                        "Error al comunicarse con el servidor de redención",
                        { type: 'danger' }
                    );
                }

                try {
                    const orderline = orderlines.find(ol => ol.id === product.odoo_id);
                    await this.pos.data.call(
                        "leal.redeem.response",
                        "create_from_response",
                        [this.state.redeemResponse, {
                            uid_customer: product.uid_customer,
                            id_premio: product.id_premio,
                            codigo_premio: product.codigo_premio,
                            valor_redencion: orderline?.get_price_with_tax() || 0,
                            id_comercio: this.state.commerceData.id_comercio,
                            id_sucursal: this.state.commerceData.id_sucursal,
                            odoo_ticket_code: order.ticket_code,
                            odoo_product_id: product.codigo_premio === 'DISC_LEAL' ? null : orderline.product_id.id,
                            no_factura: order.name
                        }],
                    );
                } catch (error) {
                    console.error("Error al guardar respuesta de redención:", error);
                }

                if (this.state.redeemResponse.code === 109) {
                    this.state.askForOtpData = {
                        id_comercio: product.id_comercio,
                        id_externo: String(this.pos.config.id),
                        uid_cms: this.state.commerceData.uid_cms,
                        uid: product.uid_customer
                    };
                    if (product.codigo_premio !== 'DISC_LEAL') {
                        this.state.askForOtpData.id_premio = product.id_premio;
                        this.state.askForOtpData.codigo_premio = product.codigo_premio;
                    }
                    const otpResult = await this.pos.data.call(
                        "leal.api.settings",
                        "send_otp_to_customer",
                        [this.state.askForOtpData],
                        {}
                    );
                    if (parseInt(otpResult.code) !== 100) {
                        this.env.services.ui.unblock();
                        this.env.services.notification.add(
                            'Error al enviar OTP al cliente, inténtelo de nuevo',
                            { type: 'danger' }
                        );
                        return;
                    }
                    this.env.services.ui.unblock();
                    const responseOtp = await makeAwaitable(this.dialog, OTPInputPopup, {
                        title: _t("Código OTP inválido"),
                        body: _t("El código OTP ingresado no es válido. Por favor, ingréselo nuevamente."),
                        confirmText: _t("Validar"),
                        resendText: _t("Reenviar"),
                        cancelText: _t("Cancelar")
                    });
                    if (!responseOtp || responseOtp === undefined || responseOtp === "") {
                        this.env.services.notification.add(
                            "Código OTP requerido para completar la redención Leal",
                            { type: 'warning' }
                        );
                        this.env.services.ui.unblock();
                        return;
                    }
                    else if (responseOtp && responseOtp.length === 4) {

                        otp_value = responseOtp;
                        product.otp_value = otp_value;
                        product.redimido = false;
                        this.state.lealRedeemData = this.state.lealRedeemData.filter(p => {
                            if (p.codigo_premio === 'DISC_LEAL') {
                                p.otp_value = otp_value;
                                p.redimido = false;

                                return p;
                            }
                            else if (p.odoo_id === product.odoo_id.id && p.odoo_order_uuid === product.odoo_order_uuid) {
                                p.otp_value = otp_value;
                                p.redimido = false;
                            }
                            return p;
                        });
                        localStorage.setItem('leal_redeem_data', JSON.stringify(this.state.lealRedeemData));
                        setTimeout(() => {
                            this.validateOrder(isForceValidate);
                        }, 500);
                        return;
                    }
                    else {
                        this.env.services.notification.add(
                            "Código OTP requerido para completar la redención Leal",
                            { type: 'warning' }
                        );
                        this.env.services.ui.unblock();
                        return;
                    }
                }
                if (this.state.redeemResponse.code !== 100) {
                    this.env.services.notification.add(
                        `No fue posible redimir los puntos: ${this.state.redeemResponse.message || 'Error desconocido'}`,
                        { type: 'danger' }
                    );
                    this.env.services.ui.unblock();
                    return;
                }
                product.redimido = true;
                this.state.lealRedeemData = this.state.lealRedeemData.filter(p => {
                    if (p.odoo_id === product.odoo_id && p.odoo_order_uuid === product.odoo_order_uuid) {
                        p.redimido = true;
                    }
                    return p;
                });
                localStorage.setItem('leal_redeem_data', JSON.stringify(this.state.lealRedeemData));
                this.env.services.notification.add(
                    "Puntos Leal redimidos exitosamente",
                    { type: 'success' }
                );
            }
        }

        this.env.services.ui.unblock();
        localStorage.removeItem("leal_redeem_data");
        return super.validateOrder(isForceValidate);
    },

    async validateCampaignsOnLoad() {
        this.env.services.ui.block();
        const order = this.pos.get_order();
        if (!order) {
            this.env.services.ui.unblock();
            return;
        }
        // Obtener el cliente de la orden
        const customer = order.get_partner();
        if (!customer) {
            this.env.services.ui.unblock();
            return;
        }
        try {
            // Obtener campañas activas desde la API de Leal
            const campaigns = await this.getCampaigns();
            if (!campaigns || campaigns.length === 0) {
                this.env.services.ui.unblock();
                return;
            }

            // Validar cada campaña
            for (const campaign of campaigns) {
                await this.validateProductCampaign(campaign, order);
            }

        } catch (error) {
            this.env.services.ui.unblock();
            console.error("Error durante la validación de campañas:", error);
        } finally {
            this.env.services.ui.unblock();
        }
    },

    /**
     * Obtiene las campañas activas desde el modelo leal.customer.campaign
     */
    async getCampaigns() {
        try {
            const campaigns = await this.pos.data.call(
                "leal.customer.campaign",
                "search_read",
                [[['active', '=', true]]],
                {
                    fields: [
                        'id',
                        'rule_type',
                        'reward_type',
                        'requirement_id',
                        'minimum_quantity',
                        'minimum_amount',
                        'max_discount_amount',
                        'benefit_unit_limit',
                        'reward',
                        'campaign_name',
                        'promotion_code',
                        'campaign_id'
                    ]
                }
            );
            return campaigns || [];
        } catch (error) {
            console.error("Error al obtener campañas activas:", error);
            return [];
        }
    },

    /**
     * Valida una campaña de tipo producto
     */
    async validateProductCampaign(campaign, order) {

        try {
            // Validación para producto - producto
            // NOTE: Revisado V18.0
            if (campaign.rule_type === 'product' && campaign.reward_type === 'product') {
                const orderlines = order.get_orderlines();
                const hasRequiredProduct = orderlines.some(line =>
                    line.product_id.default_code === campaign.requirement_id
                );

                if (!hasRequiredProduct) {
                    return;
                }
                const requiredProduct = await this.findProductByCode(campaign.requirement_id);
                if (!requiredProduct) {
                    return;
                }

                // Buscar el producto de recompensa en Odoo
                let rewardProduct = await this.findProductByCode(campaign.reward);
                if (!rewardProduct) {
                    this.env.services.notification.add(
                        `No se ha podido aplicar la promoción ${campaign.campaign_name} debido a que no existe el producto premio: SKU ${campaign.reward}`,
                        { type: 'warning', sticky: true, }
                    );
                    return;
                }

                // Verificar la cantidad del producto requerido en la orden
                const requiredQuantity = this.getProductQuantityInOrder(order, requiredProduct.id);
                if (requiredQuantity >= campaign.minimum_quantity && requiredQuantity <= campaign.benefit_unit_limit) {
                    let hasProducts = orderlines.filter(p => p.product_id.default_code === campaign.requirement_id);
                    let totalRelatedProducts = 0;
                    if (hasProducts) {
                        orderlines.forEach(product => {
                            totalRelatedProducts += product.get_price_with_tax();
                            if (product.product_id.default_code === campaign.requirement_id) {
                                updateProductsToCampaign(product);
                            }
                        })
                    }
                    this.state.hasAccumulatePoints = true;
                    await this.addRewardProductToOrder(order, rewardProduct, campaign, totalRelatedProducts);
                } else {
                    this.env.services.notification.add(
                        `No se ha podido aplicar la promoción "${campaign.campaign_name}" debido a que la cantidad de ${requiredProduct.default_code} en la orden es de ${requiredQuantity}, la cantidad mínima es de ${campaign.minimum_quantity} y la cantidad máxima es de ${campaign.benefit_unit_limit}`,
                        { type: 'warning', sticky: true, }
                    );
                }
            }
            // NOTE: Revisado V18.0
            // Validación producto - discount
            else if (campaign.rule_type === 'product' && campaign.reward_type === 'discount') {
                const orderlines = order.get_orderlines();
                const hasRequiredProduct = orderlines.filter(line =>
                    line.product_id.default_code === campaign.requirement_id
                );

                if (hasRequiredProduct.length === 0) {
                    return;
                }
                const requiredProduct = await this.findProductByCode(campaign.requirement_id);
                if (!requiredProduct) {
                    return;
                }
                let amount = hasRequiredProduct.reduce((acc, p) => acc + p.get_price_with_tax(), 0);

                // Verificar la cantidad del producto requerido en la orden
                const requiredQuantity = this.getProductQuantityInOrder(order, requiredProduct.id);
                const qtyCheck = requiredQuantity >= campaign.minimum_quantity && requiredQuantity <= campaign.benefit_unit_limit;
                const amountCheck = amount >= campaign.minimum_amount;
                if (qtyCheck && amountCheck) {
                    // Agregar el producto de recompensa a la orden
                    this.state.hasAccumulatePoints = true;
                    await this.addDiscountToOrder(order, campaign, requiredProduct);
                } else {
                    this.env.services.notification.add(
                        `No se ha podido aplicar la promoción "${campaign.campaign_name}" debido a que el monto total (COP ${amount}) o la cantidad (${requiredQuantity}) no coincide con los requisitos`,
                        { type: 'warning', sticky: true, }
                    );
                    orderlines.forEach(line => {
                        if ("DISC_LEAL" === line.product.default_code) {
                            order.removeOrderline(line);
                        }
                    })
                }
            }
            // NOTE: Revisado V18.0
            // Validación categoría - discount
            else if (campaign.rule_type === 'category' && campaign.reward_type === 'discount') {
                // Validar si hay productos en la orden que pertenezcan a la categoría requerida
                const orderlines = order.get_orderlines();
                const hasProductsInCategory = await this.hasProductsInCategory(orderlines, campaign.requirement_id);

                if (!hasProductsInCategory) {
                    return;
                }

                const categoryTotal = await this.getCategoryTotalInOrder(orderlines, campaign.requirement_id);
                // Verificar si cumple con el monto mínimo
                if (campaign.minimum_amount && categoryTotal < campaign.minimum_amount) {
                    this.env.services.notification.add(
                        `No se ha podido aplicar la promoción "${campaign.campaign_name}" debido a que el total de la categoría ${campaign.requirement_id} es de ${categoryTotal}, el monto mínimo es de ${campaign.minimum_amount}`,
                        { type: 'warning', sticky: true, }
                    );
                    orderlines.forEach(line => {
                        if ("DISC_LEAL" === line.product.default_code) {
                            order.removeOrderline(line);
                        }
                    })
                    this.state.hasAccumulatePoints = false;
                    return;
                }
                // Aplicar descuento
                this.state.hasAccumulatePoints = true;
                await this.addDiscountToOrder(order, campaign, null, categoryTotal);
            }
            // Validación orden - discount
            // NOTE: Revisado V18.0
            else if (campaign.rule_type === 'order' && campaign.reward_type === 'discount') {
                const orderTotal = order.get_subtotal();
                if (orderTotal >= campaign.minimum_amount) {
                    const discount = orderTotal * (campaign.discount / 100)
                    if (discount > campaign.max_discount_amount) {
                        discount = campaign.max_discount_amount
                    }
                    order.get_orderlines().forEach(line => {
                        updateProductsToCampaign(line)
                    })
                    this.state.hasAccumulatePoints = true;
                    await this.addDiscountToOrder(order, campaign, null, orderTotal);
                }
                else {
                    orderlines.forEach(line => {
                        if ("DISC_LEAL" === line.product.default_code) {
                            order.removeOrderline(line);
                        }
                    })
                }
            }

        } catch (error) {
            console.error(`Error validando campaña ${campaign.id}:`, error);
        }
    },

    /**
     * Busca un producto en Odoo por su código por defecto
     */
    async findProductByCode(defaultCode) {
        try {
            const products = await this.pos.data.call(
                "product.product",
                "search_read",
                [[['default_code', '=', defaultCode], ['available_in_pos', '=', true]]],
                {
                    fields: ['id', 'name', 'default_code', 'list_price'],
                    limit: 1
                }
            );

            return products && products.length > 0 ? products[0] : null;
        } catch (error) {
            console.error(`Error buscando producto ${defaultCode}:`, error);
            return null;
        }
    },

    /**
     * Obtiene la cantidad total de un producto en la orden actual
     */
    getProductQuantityInOrder(order, productId) {
        const orderlines = order.get_orderlines();
        let totalQuantity = 0;

        for (const line of orderlines) {
            if (line.product_id.id === productId) {
                totalQuantity += line.get_quantity();
                updateProductsToCampaign(line);
            }
        }

        return totalQuantity;
    },

    /**
     * Agrega el producto de recompensa a la orden
     */
    async addRewardProductToOrder(order, rewardProduct, campaign, benefit_amount) {
        try {
            // Verificar si el producto de recompensa ya está en la orden
            const existingLine = order.get_orderlines().find(line => line.product_id.id === rewardProduct.id);

            if (existingLine) {
                return;
            }

            const posProduct = this.pos.models['product.product'].find(p => p.id === rewardProduct.id || p.barcode === rewardProduct.id);
            if (!posProduct) {
                return;
            }

            // Agregar el producto a la orden con precio 0 (recompensa gratuita)
            await reactive(this.pos).addLineToCurrentOrder({ product_id: posProduct.id });
            const selectedLine = order.get_selected_orderline();
            if (selectedLine) {
                selectedLine.set_unit_price(0);
                selectedLine.set_discount(100);
                const lealRedemptionData = {
                    is_campaign_reward: true,
                    campaign_id: campaign.campaign_id || null,
                    promotion_code: campaign.promotion_code || null,
                    benefit_amount: benefit_amount,
                    has_accumulated: false,
                    odoo_id: selectedLine.id || null,
                    odoo_order_uuid: order.uuid || null,
                    product_id: rewardProduct.id || null,
                };
                const lealCampaignRedeemData = localStorage.getItem('leal_campaign_redeem_data') ? JSON.parse(localStorage.getItem('leal_campaign_redeem_data')) : [];
                lealCampaignRedeemData.push(lealRedemptionData);
                localStorage.setItem('leal_campaign_redeem_data', JSON.stringify(lealCampaignRedeemData));
            }


            // Mostrar notificación al usuario
            this.env.services.notification.add(
                `Se ha agregado el producto ${rewardProduct.name} a la orden. Campaña: ${campaign.campaign_name}`,
                { type: 'success', sticky: true, }
            );
        } catch (error) {
            console.error(`Error agregando producto de recompensa:`, error);
        }
    },

    /**
     * Verifica si hay productos en la orden que pertenezcan a una categoría específica
     */
    async hasProductsInCategory(orderlines, categoryName) {
        for (const line of orderlines) {
            const productCategories = await this.getProductCategories(line.product_id.id, categoryName);
            if (productCategories) {
                return true;
            }
        }
        return false;
    },

    /**
     * Obtiene las categorías de un producto
     */
    async getProductCategories(productId, categoryName) {
        try {
            const product = await this.pos.data.call(
                "product.product",
                "get_product_if_in_pos_category",
                [productId, categoryName],
                {}
            );
            return product.id !== undefined ? product : null

        } catch (error) {
            console.error(`Error obteniendo categorías del producto ${productId}:`, error);
            return [];
        }
    },

    /**
     * Calcula el total de productos de una categoría específica en la orden
     */
    async getCategoryTotalInOrder(orderlines, categoryName) {
        let total = 0;
        for (const line of orderlines) {
            const productCategories = await this.getProductCategories(line.product_id.id, categoryName);
            if (productCategories) {
                updateProductsToCampaign(line);
                total += line.get_price_with_tax();
            }
        }
        return total;
    },

    async addDiscountToOrder(order, campaign, requiredProduct, categoryTotal = 0) {
        if (this._addingDiscount) {
            return;
        }

        // Calcular monto de descuento y beneficio antes de cualquier early return
        const discountPercentage = parseFloat(campaign.reward) || 0;
        let discountAmount = 0;
        let benefit_amount = 0;
        if (categoryTotal > 0) {
            discountAmount = (categoryTotal * discountPercentage) / 100;
            benefit_amount = categoryTotal - discountAmount;
        } else {
            const productTotal = requiredProduct ? requiredProduct.list_price : 0;
            discountAmount = (productTotal * discountPercentage) / 100;
            benefit_amount = productTotal - discountAmount;
        }

        if (campaign.max_discount_amount && discountAmount > campaign.max_discount_amount) {
            discountAmount = campaign.max_discount_amount;
        }

        // Si el descuento es nulo o negativo, no continuar
        if (discountAmount <= 0) {
            return;
        }

        // Verificar si ya existe una línea DISC_LEAL en la orden
        const hasExisting = order.get_orderlines().some(line => {
            return (line.product && line.product.default_code === 'DISC_LEAL') ||
                (line.product_id && line.product_id.default_code === 'DISC_LEAL');
        });

        // Si ya existe, sincronizar las líneas DISC_LEAL presentes en la orden al localStorage y salir
        if (hasExisting) {
            const lealCampaignRedeemData = localStorage.getItem('leal_campaign_redeem_data') ? JSON.parse(localStorage.getItem('leal_campaign_redeem_data')) : [];

            const orderlines = order.get_orderlines();
            const discountLinesInOrder = orderlines.filter(line => {
                return (line.product && line.product.default_code === 'DISC_LEAL') ||
                    (line.product_id && line.product_id.default_code === 'DISC_LEAL');
            });

            for (const line of discountLinesInOrder) {
                const lineId = line.id || null;
                const lineUuid = line.uuid || null;
                const productId = (line.product && line.product.id) || (line.product_id && line.product_id.id) || null;

                const exists = lealCampaignRedeemData.some(item => item.is_campaign_reward && (
                    item.odoo_id === lineId ||
                    item.odoo_order_uuid === lineUuid ||
                    item.product_id === productId
                ));

                if (!exists) {
                    lealCampaignRedeemData.push({
                        is_campaign_reward: true,
                        campaign_id: campaign.campaign_id || null,
                        promotion_code: campaign.promotion_code || null,
                        benefit_amount: benefit_amount,
                        has_accumulated: false,
                        odoo_id: lineId,
                        odoo_order_uuid: lineUuid,
                        product_id: productId,
                    });
                }
            }

            localStorage.setItem('leal_campaign_redeem_data', JSON.stringify(lealCampaignRedeemData));
            return;
        }

        this._addingDiscount = true;
        try {
            // discountAmount y benefit_amount ya calculados arriba

            let discountProducts = await this.pos.data.call(
                "product.product",
                "search_read",
                [[['default_code', '=', 'DISC_LEAL']]],
                {
                    fields: ['id'],
                    limit: 1
                }
            );

            if (!discountProducts || discountProducts.length === 0) {
                this.env.services.notification.add(
                    `No es posible agregar descuento para la campaña ${campaign.campaign_name} debido a que el descuento con referencia interna 'DISC_LEAL' no fue encontrado.`,
                    { type: 'warning', sticky: true, }
                );
                return;
            }

            const stillHasExisting = order.get_orderlines().some(line => {
                return (line.product && line.product.default_code === 'DISC_LEAL') ||
                    (line.product_id && line.product_id.default_code === 'DISC_LEAL');
            });
            if (stillHasExisting) {
                // En caso de carrera, volver a sincronizar por seguridad
                const lealCampaignRedeemData = localStorage.getItem('leal_campaign_redeem_data') ? JSON.parse(localStorage.getItem('leal_campaign_redeem_data')) : [];
                const orderlines = order.get_orderlines();
                const discountLinesInOrder = orderlines.filter(line => {
                    return (line.product && line.product.default_code === 'DISC_LEAL') ||
                        (line.product_id && line.product_id.default_code === 'DISC_LEAL');
                });
                for (const line of discountLinesInOrder) {
                    const lineId = line.id || null;
                    const lineUuid = line.uuid || null;
                    const productId = (line.product && line.product.id) || (line.product_id && line.product_id.id) || null;

                    const exists = lealCampaignRedeemData.some(item => item.is_campaign_reward && (
                        item.odoo_id === lineId ||
                        item.odoo_order_uuid === lineUuid ||
                        item.product_id === productId
                    ));

                    if (!exists) {
                        lealCampaignRedeemData.push({
                            is_campaign_reward: true,
                            campaign_id: campaign.campaign_id || null,
                            promotion_code: campaign.promotion_code || null,
                            benefit_amount: benefit_amount,
                            has_accumulated: false,
                            odoo_id: lineId,
                            odoo_order_uuid: lineUuid,
                            product_id: productId,
                        });
                    }
                }
                localStorage.setItem('leal_campaign_redeem_data', JSON.stringify(lealCampaignRedeemData));
                return;
            }

            await reactive(this.pos).addLineToCurrentOrder({ product_id: discountProducts[0].id });

            const orderlines = order.get_orderlines();
            let discountLine = orderlines.find(line => {
                return (line.product && line.product.default_code === 'DISC_LEAL') ||
                    (line.product_id && line.product_id.default_code === 'DISC_LEAL');
            });

            const allDiscountLines = orderlines.filter(line => {
                return (line.product && line.product.default_code === 'DISC_LEAL') ||
                    (line.product_id && line.product_id.default_code === 'DISC_LEAL');
            });
            if (allDiscountLines.length > 1) {
                for (let i = 1; i < allDiscountLines.length; i++) {
                    try { order.removeOrderline(allDiscountLines[i]); } catch (_) { }
                }
                discountLine = allDiscountLines[0];
            }

            const selectedLine = order.get_selected_orderline();
            if (selectedLine && ((selectedLine.product && selectedLine.product.default_code === 'DISC_LEAL') || (selectedLine.product_id && selectedLine.product_id.default_code === 'DISC_LEAL'))) {
                selectedLine.set_unit_price(-discountAmount);
            } else if (discountLine) {
                try {
                    discountLine.set_unit_price(-discountAmount);
                } catch (_) { }
            }

            if (discountLine) {
                try {
                    discountLine.set_customer_note(`Descuento por campaña: ${campaign.campaign_name} (${discountPercentage}%)`);
                } catch (_) { }
            }

            // Ahora sincronizar todas las líneas DISC_LEAL en la orden al localStorage (evitar duplicados)
            const lealCampaignRedeemDataFinal = localStorage.getItem('leal_campaign_redeem_data') ? JSON.parse(localStorage.getItem('leal_campaign_redeem_data')) : [];
            const discountLinesInOrderFinal = order.get_orderlines().filter(line => {
                return (line.product && line.product.default_code === 'DISC_LEAL') ||
                    (line.product_id && line.product_id.default_code === 'DISC_LEAL');
            });

            for (const line of discountLinesInOrderFinal) {
                const lineId = line.id || null;
                const lineUuid = line.uuid || null;
                const productId = (line.product && line.product.id) || (line.product_id && line.product_id.id) || null;

                const exists = lealCampaignRedeemDataFinal.some(item => item.is_campaign_reward && (
                    item.odoo_id === lineId ||
                    item.odoo_order_uuid === lineUuid ||
                    item.product_id === productId
                ));

                if (!exists) {
                    lealCampaignRedeemDataFinal.push({
                        is_campaign_reward: true,
                        campaign_id: campaign.campaign_id || null,
                        promotion_code: campaign.promotion_code || null,
                        benefit_amount: benefit_amount,
                        has_accumulated: false,
                        odoo_id: lineId,
                        odoo_order_uuid: lineUuid,
                        product_id: productId,
                    });
                }
            }

            localStorage.setItem('leal_campaign_redeem_data', JSON.stringify(lealCampaignRedeemDataFinal));

            this.env.services.notification.add(
                `Se ha agregado el descuento a la orden. Campaña: ${campaign.campaign_name} - Descuento: $${discountAmount.toFixed(2)}`,
                { type: 'success', sticky: true, }
            );
        } finally {
            this._addingDiscount = false;
        }
    },

    // Método para agregar una nueva línea de pago leal
    // Validar si el comercio permite redención abierta
    // Si no, mostrar mensaje de error y no agregar la línea de pago
    async addNewPaymentLine(paymentMethod) {
        this.env.services.ui.block();
        const order = this.pos.get_order();
        // Si es un reembolso, permitir agregar la línea de pago sin las validaciones de Leal.
        if (isRefund(order)) {
            super.addNewPaymentLine(paymentMethod);
            this.env.services.ui.unblock();
            return;
        }
        if (paymentMethod.name.toLowerCase() === 'leal' || paymentMethod.code === 'leal') {
            try {
                if (this.state.redencion_abierta === 0) {
                    this.env.services.notification.add(
                        "No está permitido usar el método de pago Leal en este comercio.",
                        { type: 'danger' }
                    );
                    this.env.services.ui.unblock();
                    return;
                }

                const token = await validateToken(this.pos, this.env);
                if (!token) {
                    this.env.services.ui.unblock();
                    return;
                }
                const customer = await validateCustomer(this.pos, this.dialog, this.env);
                if (!customer) {
                    this.env.services.ui.unblock();
                    return;
                }
                const amountToRedeem = await calculateAuthValue(this.env, this.pos, customer);
                if (amountToRedeem === undefined || amountToRedeem <= 0) {
                    return;
                }

                await validateIfExistsOTP(this.env, this.pos, this.dialog, customer, amountToRedeem, paymentMethod);


            } catch (error) {
                this.env.services.ui.unblock();
                console.error("Error en el flujo de pago Leal:", error);
                this.env.services.notification.add(
                    "Ocurrió un error al procesar el pago con Leal.",
                    { type: 'danger' }
                );
            }
            this.env.services.ui.unblock();
            this.state.lealRedeemData = localStorage.getItem('leal_redeem_data') ? JSON.parse(localStorage.getItem('leal_redeem_data')) : [];
            return;
        }
        this.env.services.ui.unblock();

        super.addNewPaymentLine(paymentMethod);
    },

    // Método que valida si hay redención por campañas y acumula puntos
    async accumulatePoints(order) {
        let acumlationData = {};
        let acumlationItems = [];
        let totalAcum = 0;
        const lealCampaignData = localStorage.getItem('leal_campaign_redeem_data') ? JSON.parse(localStorage.getItem('leal_campaign_redeem_data')) : [];
        lealCampaignData.forEach(campaign => {
            if (campaign.is_campaign && !campaign.has_accumulated) {
                totalAcum += campaign.precioTotal;
                acumlationItems.push(campaign);
            }
        });


        if (acumlationItems.length === 0) {
            return true;
        }

        const odooPartner = order.get_partner();
        const lealCustomer = await this.pos.data.call(
            "leal.api.settings",
            "search_customer",
            [odooPartner.vat],
            {}
        );
        let lealCustomerUid = null;
        let lealUser = null;

        if (lealCustomer.success && lealCustomer.data && lealCustomer.data.length > 0) {
            lealUser = lealCustomer.data[lealCustomer.data.length - 1];
            lealCustomerUid = lealUser.uid;
        } else {
            return false;
        }

        acumlationData["totalAcum"] = totalAcum;
        acumlationData["uid"] = lealCustomerUid;
        acumlationData["id_externo"] = this.pos.config.id;
        acumlationData["transaccion"] = {};
        acumlationData["transaccion"]["clave"] = order.uuid;
        acumlationData["transaccion"]["noFactura"] = order.pos_reference + " " + Date.now();
        acumlationData["transaccion"]["fecha"] = order.date_order;
        acumlationData["transaccion"]["fechaApertura"] = order.date_order;
        acumlationData["transaccion"]["fechaCierre"] = order.date_order;
        acumlationData["transaccion"]["totalPersonas"] = 1;
        acumlationData["transaccion"]["formaPago"] = order.payment_ids[0].payment_method_id.name; //
        acumlationData["transaccion"]["codVendedor"] = order.user_id.id;
        acumlationData["transaccion"]["subTotal"] = order.get_total_with_tax();
        acumlationData["transaccion"]["propina"] = 0;
        acumlationData["transaccion"]["total"] = order.get_total_with_tax();
        acumlationData["transaccion"]["impuestoTotal"] = order.get_total_tax();
        acumlationData["transaccion"]["descuentoTotal"] = order.get_total_discount();
        acumlationData["transaccion"]["items"] = acumlationItems;

        try {
            return await redeemCampaign(this.env, order, lealCustomerUid, acumlationData);
        }
        catch (e) {
            console.error(e);
            return false;
        }
    }
});
