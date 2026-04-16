/** @odoo-module */

import { PartnerList } from "@point_of_sale/app/screens/partner_list/partner_list";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { _t } from "@web/core/l10n/translation";

/**
 * Patch PartnerList to enhance the getPartners method for dynamic search
 * and override searchPartner for server-side search when needed
 */
patch(PartnerList.prototype, {
    setup() {
        super.setup();
        this.pos = usePos();
        this.dynamicSearch = useService("sbl_dynamic_search");
        this.searchState = {
            lastQuery: null,
            hasSearchedServer: false,
        };
    },

    /**
     * Override getPartners to add dynamic search capability
     * This method is called when user types in the search box
     */
    getPartners() {
        const partners = super.getPartners();

        // If speedup is enabled and no local results found, suggest server search
        if (this.pos && this.pos.config && this.pos.config.sbl_enable_pos_speedup &&
            partners.length === 0 &&
            this.state.query &&
            this.state.query.trim().length > 2) {

            // Reset search state if query changed
            if (this.searchState.lastQuery !== this.state.query) {
                this.searchState.hasSearchedServer = false;
                this.searchState.lastQuery = this.state.query;
            }

            // If we haven't searched server for this query yet, trigger async search
            if (!this.searchState.hasSearchedServer) {
                this._triggerServerSearch();
            }
        }

        return partners;
    },

    /**
     * Trigger server search asynchronously without blocking the UI
     */
    async _triggerServerSearch() {
        if (!this.state.query || this.searchState.hasSearchedServer) {
            return;
        }

        this.searchState.hasSearchedServer = true;

        try {
            const result = await this.dynamicSearch.searchPartners(this.state.query, this.pos.config.id, 50);

            if (result.error) {
                console.warn("Dynamic partner search error:", result.error);
                return;
            }

            if (result.partners && result.partners.length > 0) {
                // Filter out partners that already exist in POS models
                const newPartners = result.partners.filter(
                    (p) => !this.pos.models["res.partner"].get(p.id)
                );

                // Use loadData() to properly link Many2one relationships (pricelist, fiscal position)
                if (newPartners.length > 0) {
                    this.pos.models.loadData({ "res.partner": newPartners });

                    // Force re-render to show new partners
                    this.render();

                    this.notification.add(
                        _t("Found %s additional customer(s) from database.", newPartners.length),
                        3000
                    );
                }
            }
        } catch (error) {
            console.error("Dynamic partner search failed:", error);
        }
    },

    /**
     * Override searchPartner to use our dynamic search when "Enter" is pressed or "Load More" is clicked
     */
    async searchPartner() {
        if (this.pos && this.pos.config && this.pos.config.sbl_enable_pos_speedup) {
            // Use our enhanced search method for explicit searches
            return await this._sblSearchPartner();
        } else {
            // Use standard Odoo method
            return await super.searchPartner();
        }
    },

    async _sblSearchPartner() {
        if (!this.state.query || this.state.query.trim() === "") {
            return [];
        }

        try {
            const result = await this.dynamicSearch.searchPartners(this.state.query, this.pos.config.id, 50);

            if (result.error) {
                console.warn("Dynamic partner search error:", result.error);
                // Fallback to standard method
                return await super.searchPartner();
            }

            if (result.partners && result.partners.length > 0) {
                // Filter out partners that already exist in POS models
                const newPartners = result.partners.filter(
                    (p) => !this.pos.models["res.partner"].get(p.id)
                );

                // Use loadData() to properly link Many2one relationships (pricelist, fiscal position)
                if (newPartners.length > 0) {
                    this.pos.models.loadData({ "res.partner": newPartners });

                    this.notification.add(
                        _t("Found %s additional customer(s) from database.", newPartners.length),
                        3000
                    );
                }

                // Return the found partners
                return result.partners.map(p => this.pos.models["res.partner"].get(p.id)).filter(Boolean);
            } else {
                return [];
            }
        } catch (error) {
            console.error("Dynamic partner search failed:", error);
            // Fallback to standard method
            return await super.searchPartner();
        }
    }
});
