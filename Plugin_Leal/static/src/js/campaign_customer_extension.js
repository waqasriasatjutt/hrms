/** @odoo-module **/

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { CampaignDetailsPopup } from "./campaign_details_popup";
import { _t } from "@web/core/l10n/translation";
// import { useService } from "@web/core/utils/hooks";

patch(ProductScreen.prototype, {
    setup() {
        super.setup();
        this.pos = usePos();
        // this.state = useState({
        //     // lealUser: null,
        //     // customerUID: null,
        // });
        // this.rpc = useService("rpc");
        // this.popup = useService("popup");
        this._originalSetPartner = this.currentOrder.set_partner.bind(this.currentOrder);


        this.currentOrder.set_partner = (partner) => {
            const previousPartner = this.currentOrder.get_partner();

            const result = this._originalSetPartner(partner);

            if (partner && (!previousPartner || previousPartner.id !== partner.id)) {
                this.validateCustomerCampaign(partner);
            }
            else {
                this.validateCustomerCampaign(partner);
            }

            return result;
        };
    },

    async validateCustomerCampaign(partner) {
        this.env.services.ui.block();
        if (!partner) {
            this.env.services.ui.unblock();
            console.warn("No se proporcionó un cliente. Abortando la operación.");
            return false;
        }

        // Verificar si el componente sigue activo
        if (this.__owl__.status === 5) { // 5 = destroyed
            this.env.services.ui.unblock();
            console.warn("El componente ProductScreen ha sido destruido. Abortando la operación.");
            return false;
        }

        try {
            const customerSearchResult = await this.pos.data.call(
                "leal.api.settings",
                "search_customer",
                [partner.vat],
                {}
            );

            let lealUser = null;
            let customerUID = null;

            if (customerSearchResult.success && customerSearchResult.data && customerSearchResult.data.length > 0) {
                lealUser = customerSearchResult.data[customerSearchResult.data.length - 1];
                customerUID = lealUser.uid;
            } else {
                this.env.services.ui.unblock();
                console.error("Error al buscar cliente en Leal:", customerSearchResult);
                return false;
            }

            // Verificar nuevamente si el componente sigue activo antes de la segunda llamada RPC
            if (this.__owl__.status === 5) {
                this.env.services.ui.unblock();
                console.warn("El componente ProductScreen ha sido destruido. Abortando la operación.");
                return false;
            }

            const customerCampaigns = await this.pos.data.call(
                "leal.api.settings",
                "search_costumer_campaigns",
                [customerUID],
                {}
            );

            if (customerCampaigns.statusCode === 200 && customerCampaigns.data && customerCampaigns.data.length > 0) {
                // Verificar nuevamente si el componente sigue activo antes de la tercera llamada RPC
                if (this.__owl__.status === 5) {
                    this.env.services.ui.unblock();
                    return false;
                }

                // Guardar las campañas del cliente en la base de datos
                try {
                    const saveResult = await this.pos.data.call(
                        "leal.customer.campaign",
                        "save_customer_campaigns",
                        [customerUID, customerCampaigns.data, this.pos.config.id],
                        {}
                    );

                    if (saveResult.success) {
                        // Verificar si el componente sigue activo antes de mostrar el popup
                        if (this.__owl__.status !== 5) {
                            this.showCampaignDetailsPopup(customerCampaigns.data);
                        }
                    } else {
                        this.env.services.ui.unblock();
                        console.error("Error al guardar campañas:", saveResult.message);
                    }
                } catch (error) {
                    this.env.services.ui.unblock();
                    console.error("Error al guardar campañas del cliente:", error);
                }
            } else {
                this.env.services.ui.unblock();
                console.error("Error al obtener campañas del cliente:", customerCampaigns);
            }
            this.env.services.ui.unblock();
            return false;
        } catch (error) {
            this.env.services.ui.unblock();
            console.error("Error en la validación de campañas:", error);
            return false;
        }
    },

    async showCampaignDetailsPopup(campaigns) {
        this.env.services.ui.block();
        if (!campaigns || campaigns.length === 0) {
            this.env.services.ui.unblock();
            return;
        }

        if (this.__owl__.status === 5) {
            this.env.services.ui.unblock();
            return;
        }

        try {
            this.env.services.ui.unblock();
            await makeAwaitable(this.env.services.dialog, CampaignDetailsPopup, {
                title: _t("Campañas Leal Disponibles"),
                campaigns: campaigns,
            });
        } catch (error) {
            this.env.services.ui.unblock();
            console.error("Error al mostrar popup de campañas:", error);
        }
    }
});