/** @odoo-module */

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { _t } from "@web/core/l10n/translation";

/**
 * Patch ProductScreen to enhance the product search functionality
 * to work with our speedup configuration
 */
patch(ProductScreen.prototype, {
    setup() {
        super.setup();
        this.pos = usePos();
        this.dynamicSearch = useService("sbl_dynamic_search");
        this.searchState = {
            lastSearchWord: null,
            hasSearchedServer: false,
        };
    },

    /**
     * Override getProductsBySearchWord to add dynamic search capability
     * This method is called when user types in the search box
     */
    getProductsBySearchWord(searchWord) {
        const localResults = super.getProductsBySearchWord(searchWord);
        
        // If speedup is enabled and no local results found, trigger server search
        if (this.pos && this.pos.config && this.pos.config.sbl_enable_pos_speedup && 
            localResults.length === 0 && 
            searchWord && 
            searchWord.trim().length > 2) {
            
            // Reset search state if query changed
            if (this.searchState.lastSearchWord !== searchWord) {
                this.searchState.hasSearchedServer = false;
                this.searchState.lastSearchWord = searchWord;
            }
            
            // If we haven't searched server for this query yet, trigger async search
            if (!this.searchState.hasSearchedServer) {
                this._triggerProductServerSearch(searchWord);
            }
        }
        
        return localResults;
    },

    /**
     * Trigger server search asynchronously without blocking the UI
     */
    async _triggerProductServerSearch(searchWord) {
        if (!searchWord || this.searchState.hasSearchedServer) {
            return;
        }
        
        this.searchState.hasSearchedServer = true;
        
        try {
            const product = await this.loadProductFromDB();
            
            if (product && product.length > 0) {
                // Process products using POS data service (like standard Odoo does)
                const records = {
                    'product.product': product
                };
                
                // Let POS process the data using its standard mechanisms
                // await this.pos.processData(records);
                
                // Count new products
                let addedCount = 0;
                for (const productData of product) {
                    const product = this.pos.models["product.product"].get(productData.id);
                    if (product) {
                        addedCount++;
                    }
                }
                
                if (addedCount > 0) {
                    // Force re-render to show new products
                    this.render();
                    
                    this.notification.add(
                        _t("Found %s additional product(s) from database.", addedCount),
                        3000
                    );
                }
            }
        } catch (error) {
            console.error("Dynamic product search failed:", error);
        }
    },
});