import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";
import { createRelatedModels } from "@point_of_sale/app/models/related_models";
import { PosData } from "@point_of_sale/app/models/data_service";

patch(PosData.prototype, {
    async initData() {
        const modelClasses = {};
        const relations = {};
        const fields = {};
        const data = {};
        const response = await this.loadInitialData();
        // console.log("loaded product", response['product.product']);
    
        // Step 1: Populate `relations`, `fields`, and `data`
        for (const [model, values] of Object.entries(response)) {
            relations[model] = values.relations;
            fields[model] = values.fields;
            data[model] = values.data;
        }

        // Add stock_quantity to fields and relations for product.product
        if (!fields["product.product"].includes("stock_quantity")) {
            fields["product.product"].push("stock_quantity");
        }
        relations["product.product"] = relations["product.product"] || {};
        relations["product.product"].stock_quantity = {
            name: "stock_quantity",
            type: "float",
            compute: false,
            related: false,
            default: 0
        };

        // Step 2: Populate `modelClasses` and update `relations`
        for (const posModel of registry.category("pos_available_models").getAll()) {
            const pythonModel = posModel.pythonModel;
            const extraFields = posModel.extraFields || {};
    
            modelClasses[pythonModel] = posModel;
            relations[pythonModel] = {
                ...relations[pythonModel],
                ...extraFields,
            };
        }

        // Step 3: Generate `models`, `records`, and `indexedRecords`
        const { models, records, indexedRecords } = createRelatedModels(
            relations,
            modelClasses,
            this.opts
        );
    
        this.records = records;
        this.indexedRecords = indexedRecords;
        this.fields = fields;
        this.relations = relations;
        this.models = models;
        // console.log("records", this.records);
        // console.log("records product.product", this.records["product.product"]);
        // console.log("records product entries", this.records["product.product"].entries());
        // console.log("indexedRecords", this.indexedRecords);
        // console.log("fields", this.fields);
        // console.log("relations", this.relations);
        // console.log("models", this.models);
        // console.log("records product.product", Array.from(this.records["product.product"].entries()));

       
        const order = data["pos.order"] || [];
        const orderlines = data["pos.order.line"] || [];
    
        delete data["pos.order"];
        delete data["pos.order.line"];
    
        this.models.loadData(data, this.modelToLoad);
        this.models.loadData({ "pos.order": order, "pos.order.line": orderlines });
    
        // Step 4: Fetch product quantities for all products in bulk
        const products = data["product.product"] || [];
        const productIds = products.map(product => product.id);
        const warehouse = await this.orm.call('stock.warehouse', 'search_read', [[['id', '=', response['pos.config']['data'][0].warehouse_id]]], { limit: 1 });
        const location = warehouse[0].lot_stock_id[0];
    
        // Call nt_get_product_info_pos with all product IDs at once
        const quantities = await this.orm.call("product.product", "nt_get_product_info_pos", [location, productIds]);
        
        
        // Update each product with its stock quantity
        for (const product of products) {
            product.stock_quantity = quantities[product.id] || 0;
            // this.records["product.product"].set(product.id, product); 
            if (this.records["product.product"].has(product.id)) {
                const existingProduct = this.records["product.product"].get(product.id);
                existingProduct.stock_quantity = quantities[product.id] || 0; // Update stock_quantity directly
            } else {
                // If the product doesn't exist in the records, you can add it
                product.stock_quantity = quantities[product.id] || 0; // Set the stock_quantity if adding
                this.records["product.product"].set(product.id, product); // Add the product
            }            
        }
        // this.records["product.product"] = products; // Ensure this is stored for global product access
        // console.log("Updated records product.product", Array.from(this.records["product.product"].entries()));

    
        const dbData = await this.loadIndexedDBData();
        this.loadedIndexedDBProducts = dbData ? dbData["product.product"] : [];
        this.network.loading = false;
    }
});


