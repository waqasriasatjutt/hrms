/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { Component, useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Dialog } from "@web/core/dialog/dialog";

export class CampaignDetailsPopup extends Component {
    static template = "Plugin_Leal.CampaignDetailsPopup";
    static components = { Dialog };
    static defaultProps = {
        confirmText: _t("Cerrar"),
        title: _t("Detalles de Campañas"),
        campaigns: [],
    };

    setup() {
        super.setup();
        this.pos = usePos();
        this.processedCampaigns = [];
        this.processCampaigns();
    }

    confirm() {
        this.props.close();
    }


    async processCampaigns() {
        this.processedCampaigns = await Promise.all(
            this.props.campaigns.map(campaign => this.validateCampaign(campaign))
        );

        // Forzar re-render del componente
        this.render();
    }

    async validateCampaign(campaign) {
        //campaign.promotion_code = this.hiddeCharacters(campaign.promotion_code);
        const processedCampaign = { ...campaign };

        // Validar si es un producto y buscar el producto
        if (campaign.rule_type === "product" && campaign.requirement_id) {
            try {
                // const productResult = await this.rpc("/web/dataset/call_kw", {
                //     model: "product.product",
                //     method: "search_read",
                //     args: [[["default_code", "=", campaign.requirement_id]]],
                //     kwargs: {
                //         fields: ["name", "default_code", "list_price", "categ_id"]
                //     }
                // });
                const productResult = await this.pos.data.call(
                    "product.product",
                    "search_read",
                    [[["default_code", "=", campaign.requirement_id]]],
                    { fields: ["name", "default_code", "list_price", "categ_id"] }
                );

                if (productResult && productResult.length > 0) {
                    processedCampaign.product_info = productResult[0];
                    processedCampaign.product_exists = true;
                } else {
                    processedCampaign.product_exists = false;
                    processedCampaign.product_warning = `Producto con código ${campaign.requirement_id} no encontrado en Odoo`;
                }
            } catch (error) {
                console.error("Error buscando producto:", error);
                processedCampaign.product_exists = false;
                processedCampaign.product_warning = `Error al buscar producto: ${error.message}`;
            }
        }

        // Aquí se pueden agregar más validaciones en el futuro
        // Por ejemplo: validaciones de fechas, montos, etc.

        return processedCampaign;
    }

    formatDate(dateString) {
        if (!dateString) return "N/A";
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('es-CO', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        } catch (error) {
            return dateString;
        }
    }

    formatCurrency(amount) {
        if (!amount && amount !== 0) return "N/A";
        return new Intl.NumberFormat('es-CO', {
            style: 'currency',
            currency: 'COP',
            minimumFractionDigits: 0
        }).format(amount);
    }

    getPayload() {
        return { confirmed: true };
    }

    async hiddeCharacters(promotion_code) {
        try {
            const config = await this.rpc("/web/dataset/call_kw", {
                model: "leal.api.settings",
                method: "search_read",
                args: [[['active', '=', true]]],
                kwargs: {
                    fields: ['hidden_characters'],
                    limit: 1
                }
            });
            hiddenCharacters = config[0].hidden_characters || 4;
            return promotion_code.slice(-hiddenCharacters);
        } catch (error) {
            return promotion_code.slice(-4);
        }
    }
}