/** @odoo-module **/

import { useState } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { CustomerSearchPopup } from "./customer_search_popup";
import { ProductSelectionPopup } from "./product_selection_popup";


patch(ControlButtons.prototype, {
    setup() {
        super.setup();
        this.state = useState({ partner: null });
        this.pos = usePos();
        this.dialog = useService("dialog");
        this.numberBuffer = useService("number_buffer");
        this.state = useState({ mostrarBoton: false, valor_por_punto_redencion: 0, redencion_abierta: 0, authorizedProducts: [], customerUID: null, customerName: null });
        // this.state = useState({ valor_por_punto_redencion: 0 });
        // this.state = useState({ redencion_abierta: 0 });
        // this.state = useState({ authorizedProducts: [] });
        // this.state = useState({ customerUID: null });
        // this.state = useState({ customerName: null });
        this.loadMostrarBotonConfig();
    },

    async loadMostrarBotonConfig() {
        try {
            const result = await this.pos.data.call(
                "leal.user.config",
                "search_read",
                [[["config_key", "=", "redencion_abierta"]], ["config_value_int"], 0, 1]
            );

            this.state.mostrarBoton = result.length > 0 && result[0].config_value_int !== 1;
            this.state.redencion_abierta = result.length > 0 ? result[0].config_value_int : 0;
        } catch (error) {
            console.error("Error al cargar configuración:", error);
        }
    },

    async onClick() {
        this.env.services.ui.block();
        const currentOrder = this.pos.get_order();
        let lealUser;

        // Verificar que el token está activo
        const tokenResult = await this.pos.data.call(
            "leal.api.settings",
            "get_token_for_frontend",
            [],
            {}
        );
        if (!tokenResult.success) {
            this.env.services.ui.unblock();
            let title = "Token Inválido";
            let message = `Error: ${tokenResult.message}`;

            if (!tokenResult.config_exists) {
                title = "Configuración Faltante";
                message = "No hay configuración de Leal API.\n\nDebe configurar primero:\n• URL de API\n• Usuario y contraseña";
            } else if (!tokenResult.is_authenticated) {
                title = "🔑 Autenticación Requerida";
                message = "La configuración existe pero no está autenticada.\n\n Por favor autentíquese con sus credenciales.";
            }

            message += "\n\n Vaya a:\nConfiguraciones → Técnico → Leal Redeem";

            this.dialog.add(ConfirmationDialog, {
                title: _t(title),
                body: _t(message),
            });
            return;
        }

        // Verificar si ya hay un cliente seleccionado en el POS
        const currentPartner = currentOrder.get_partner();


        if (currentPartner) {
            if (!currentPartner.vat || currentPartner.vat.trim() === '') {
                this.env.services.ui.unblock();
                this.dialog.add(ConfirmationDialog, {
                    title: _t("Documento requerido"),
                    body: _t(`El cliente ${currentPartner.name} no tiene documento configurado.\n\nPor favor configure el documento del cliente antes de continuar.`),
                });
                return;
            }
        }
        // Esta seleccionado el cliente en el pos
        if (currentPartner && currentPartner.vat) {
            const customerSearchResult = await this.pos.data.call(
                "leal.api.settings",
                "search_customer",
                [currentPartner.vat],
                {}
            );
            if (customerSearchResult.success && customerSearchResult.data && customerSearchResult.data.length > 0) {
                // NOTE: Se deja el último resultado cuando vienen duplicados
                // lealUser = customerSearchResult.data[customerSearchResult.data.length - 1];
                lealUser = customerSearchResult.data[0];
                this.state.customerUID = lealUser.uid;
                this.state.customerName = currentPartner.name;
            } else {
                this.env.services.ui.unblock();
                this.dialog.add(ConfirmationDialog, {
                    title: _t("Cliente no encontrado en Leal"),
                    body: _t(`El cliente ${currentPartner.name} con documento ${currentPartner.vat} no fue encontrado en Leal.`),
                });
                return;
            }
        }
        else {
            // No hay cliente seleccionado - mostrar popup de búsqueda
            this.env.services.ui.unblock();
            const payload = await makeAwaitable(this.dialog, CustomerSearchPopup, {
                title: _t("Buscar Cliente en Leal"),
                confirmText: _t("Buscar"),
                cancelText: _t("Cancelar"),
            });
            if (payload && payload.selectedCustomer) {
                const customerData = payload.selectedCustomer;
                // Validar que el documento existe en Odoo POS
                const odooCustomer = await this.pos.data.call(
                    "res.partner",
                    "search_read",
                    [[["vat", "=", customerData.cedula]], ['id', 'name', 'vat'], 0, 1]
                );
                if (!odooCustomer || odooCustomer.length === 0) {
                    this.dialog.add(ConfirmationDialog, {
                        title: _t("Cliente no encontrado"),
                        body: _t(`El cliente con documento ${customerData.cedula} no existe en el sistema Odoo.\n\nPor favor registre al cliente antes de continuar.`),
                    });
                    return;
                }
                const posCustomer = this.pos.models['res.partner'].find(p => p.id === odooCustomer[0].id);
                if (posCustomer) {
                    currentOrder.set_partner(posCustomer);
                }
                lealUser = customerData;
                this.state.customerUID = customerData.uid;
                this.state.customerName = customerData.fullname;
            }
            else {
                return;
            }
        }

        //Obtener el valor multiplicador por punto de redención
        const valor_por_punto_redencion = await this.pos.data.call(
            "leal.api.settings",
            "get_config_by_key",
            ['valor_por_punto_redencion']
        ) || 0;

        if (this.state.redencion_abierta === 0) {
            this.openRedemptionFlow();
        }
    },

    async openRedemptionFlow() {
        this.state.authorizedProducts = await this.pos.data.call(
            "leal.api.settings",
            "get_user_rewards",
            [this.state.customerUID]
        );

        const products = this.state.authorizedProducts.data.premios || [];
        if (products.length === 0) {
            this.env.services.ui.unblock();
            this.dialog.add(ConfirmationDialog, {
                title: _t("No hay beneficios disponibles para ") + this.state.customerName,
                body: _t("No hay beneficios disponibles para este cliente."),
            });
            return;
        }
        if (this.state.authorizedProducts.success && products && products.length > 0) {
            this.env.services.ui.unblock();
            this.dialog.add(ProductSelectionPopup, {
                title: _t("Beneficios disponibles para ") + this.state.customerName,
                products: products,
                customer_uid: this.state.customerUID,
            });
        }
        return;
    }
});
