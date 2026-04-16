/** @odoo-module */

import { registry } from "@web/core/registry";

/**
 * Dynamic Search Service for POS Speedup
 * Provides RPC calls to search products and partners not in initial load
 */
export class SBLDynamicSearchService {
    constructor(env, { orm }) {
        this.env = env;
        this.orm = orm;
        this.searchCache = new Map();
        this.cacheExpiry = 5 * 60 * 1000; // 5 minutes cache expiry
    }

    /**
     * Search for products on the server
     * @param {string} searchTerm - The search term
     * @param {number} configId - POS config ID
     * @param {number} limit - Maximum number of results
     * @returns {Promise<Object>} Search results
     */
    async searchProducts(searchTerm, configId, limit = 50) {
        const cacheKey = `product_${searchTerm}_${limit}_${configId}`;
        
        // Check cache first
        if (this.searchCache.has(cacheKey)) {
            const cached = this.searchCache.get(cacheKey);
            if (Date.now() - cached.timestamp < this.cacheExpiry) {
                return cached.data;
            }
            this.searchCache.delete(cacheKey);
        }

        try {
            // Make RPC call to product model
            const result = await this.orm.call(
                'product.product',
                'sbl_search_products_dynamic',
                [],
                {
                    config_id: configId,
                    search_term: searchTerm,
                    limit: limit
                }
            );

            // Cache the results
            this.searchCache.set(cacheKey, {
                data: result,
                timestamp: Date.now()
            });

            return result;
        } catch (error) {
            console.error("Dynamic product search failed:", error);
            return { error: error.message, products: [], count: 0 };
        }
    }

    /**
     * Search for partners on the server
     * @param {string} searchTerm - The search term
     * @param {number} configId - POS config ID
     * @param {number} limit - Maximum number of results
     * @returns {Promise<Object>} Search results
     */
    async searchPartners(searchTerm, configId, limit = 50) {
        const cacheKey = `partner_${searchTerm}_${limit}_${configId}`;
        
        // Check cache first
        if (this.searchCache.has(cacheKey)) {
            const cached = this.searchCache.get(cacheKey);
            if (Date.now() - cached.timestamp < this.cacheExpiry) {
                return cached.data;
            }
            this.searchCache.delete(cacheKey);
        }

        try {
            // Make RPC call to partner model
            const result = await this.orm.call(
                'res.partner',
                'sbl_search_partners_dynamic',
                [],
                {
                    config_id: configId,
                    search_term: searchTerm,
                    limit: limit
                }
            );

            // Cache the results
            this.searchCache.set(cacheKey, {
                data: result,
                timestamp: Date.now()
            });

            return result;
        } catch (error) {
            console.error("Dynamic partner search failed:", error);
            return { error: error.message, partners: [], count: 0 };
        }
    }

    /**
     * Clear search cache
     */
    clearCache() {
        this.searchCache.clear();
    }

    /**
     * Get cache statistics for debugging
     */
    getCacheStats() {
        return {
            size: this.searchCache.size,
            keys: Array.from(this.searchCache.keys())
        };
    }
}

// Register the service
registry.category("services").add("sbl_dynamic_search", {
    dependencies: ["orm"],
    start(env, { orm }) {
        return new SBLDynamicSearchService(env, { orm });
    },
});