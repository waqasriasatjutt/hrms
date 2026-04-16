/**
 * IndexedDB Service for POS Standalone
 * Using Dexie.js wrapper
 */

const db = new Dexie('PosStandaloneDB');

// Define schema
db.version(1).stores({
    // Master Data
    products: 'id, display_name, barcode, default_code, categ_id',
    partners: 'id, name, email, phone',
    categories: 'id, name, parent_id',
    taxes: 'id, name, amount',
    pricelists: 'id, name',
    payment_methods: 'id, name',

    // Transactional Data
    orders: '++id, name, date_order, state, partner_id',
    orderlines: '++id, order_id, product_id, qty, price_unit',
    payments: '++id, order_id, payment_method_id, amount',

    // Configuration
    config: 'key',
    sync_queue: '++id, model, operation, data, synced'
});

// Version 2: Add pricelist_items table
db.version(2).stores({
    // Master Data
    products: 'id, display_name, barcode, default_code, categ_id',
    partners: 'id, name, email, phone',
    categories: 'id, name, parent_id',
    taxes: 'id, name, amount',
    pricelists: 'id, name, active',
    pricelist_items: '++id, pricelist_id, product_id, categ_id, applied_on',
    payment_methods: 'id, name',

    // Transactional Data
    orders: '++id, name, date_order, state, partner_id',
    orderlines: '++id, order_id, product_id, qty, price_unit',
    payments: '++id, order_id, payment_method_id, amount',

    // Configuration
    config: 'key',
    sync_queue: '++id, model, operation, data, synced'
});

// Version 3: Add pos_orders for multi-tab cart management
db.version(3).stores({
    // Master Data
    products: 'id, display_name, barcode, default_code, categ_id',
    partners: 'id, name, email, phone',
    categories: 'id, name, parent_id',
    taxes: 'id, name, amount',
    pricelists: 'id, name, active',
    pricelist_items: '++id, pricelist_id, product_id, categ_id, applied_on',
    payment_methods: 'id, name',

    // Transactional Data (for sync with backend)
    orders: '++id, name, date_order, state, partner_id',
    orderlines: '++id, order_id, product_id, qty, price_unit',
    payments: '++id, order_id, payment_method_id, amount',

    // POS Orders (local cart management - multi-tab)
    pos_orders: '++id, name, created_at, updated_at, status',

    // Configuration
    config: 'key',
    sync_queue: '++id, model, operation, data, synced'
});

// Version 4: Add customers table
db.version(4).stores({
    // Master Data
    products: 'id, display_name, barcode, default_code, categ_id',
    partners: 'id, name, email, phone',
    categories: 'id, name, parent_id',
    taxes: 'id, name, amount',
    pricelists: 'id, name, active',
    pricelist_items: '++id, pricelist_id, product_id, categ_id, applied_on',
    payment_methods: 'id, name',
    customers: '++id, name, email, phone, pricelist_id',

    // Transactional Data (for sync with backend)
    orders: '++id, name, date_order, state, partner_id',
    orderlines: '++id, order_id, product_id, qty, price_unit',
    payments: '++id, order_id, payment_method_id, amount',

    // POS Orders (local cart management - multi-tab)
    pos_orders: '++id, name, created_at, updated_at, status',

    // Configuration
    config: 'key',
    sync_queue: '++id, model, operation, data, synced'
});

// Version 5: Update payment_methods schema
db.version(5).stores({
    // Master Data
    products: 'id, display_name, barcode, default_code, categ_id',
    partners: 'id, name, email, phone',
    categories: 'id, name, parent_id',
    taxes: 'id, name, amount',
    pricelists: 'id, name, active',
    pricelist_items: '++id, pricelist_id, product_id, categ_id, applied_on',
    payment_methods: '++id, name, type, active',
    customers: '++id, name, email, phone, pricelist_id',

    // Transactional Data (for sync with backend)
    orders: '++id, name, date_order, state, partner_id',
    orderlines: '++id, order_id, product_id, qty, price_unit',
    payments: '++id, order_id, payment_method_id, amount',

    // POS Orders (local cart management - multi-tab)
    pos_orders: '++id, name, created_at, updated_at, status',

    // Configuration
    config: 'key',
    sync_queue: '++id, model, operation, data, synced'
});

// Version 6: Migrate all tables to auto-increment ++id for consistency
// Data from Odoo will use xml_id mapping, so local IDs can be auto-generated
db.version(6).stores({
    // Master Data - All using ++id now
    products: '++id, xml_id, display_name, barcode, default_code, categ_id, list_price, stock_qty, active, image_1920',
    categories: '++id, xml_id, name, parent_id',
    pricelists: '++id, xml_id, name, active',
    pricelist_items: '++id, xml_id, pricelist_id, product_id, categ_id, applied_on',
    payment_methods: '++id, xml_id, name, type, active',
    customers: '++id, xml_id, name, email, phone, pricelist_id',

    // POS Orders (local cart management - multi-tab)
    // We will store lines and payments nested within the pos_order object or add dedicated local tables later if needed
    pos_orders: '++id, xml_id, name, created_at, updated_at, status',

    // We keep payments as they might be useful for separate tracking, or we can remove if strictly nested
    // User didn't ask to remove payments explicitly but usually goes with orders. 
    // I will keep payments table for now as it wasn't requested to be removed, but logically it might be unused too.
    payments: '++id, xml_id, order_id, payment_method_id, amount',

    // Configuration
    config: 'key',
    sync_queue: '++id, model, operation, data, synced'
});

/**
 * Database Migration Service
 */
class DBMigration {
    /**
     * Export entire database to JSON
     */
    async exportDB() {
        const data = {
            version: db.verno,
            timestamp: new Date().toISOString(),
            tables: {}
        };

        // Updated table list to match version 6 schema
        const tables = ['products', 'categories', 'pricelists', 'pricelist_items', 
            'payment_methods', 'customers', 'pos_orders', 'payments', 'config', 'sync_queue'];

        for (const table of tables) {
            const records = await db[table].toArray();
            
            // Migrate old data to new format
            if (table === 'products') {
                const migratedRecords = records.map(record => {
                    // Convert image_emoji to image_1920 (null for file images)
                    if (record.image_emoji) {
                        return {
                            ...record,
                            image_1920: null,  // Use file image instead of emoji
                            image_emoji: undefined  // Remove old field
                        };
                    }
                    return record;
                });
                data.tables[table] = migratedRecords;
            } else {
                data.tables[table] = records;
            }
        }

        return data;
    }

    /**
     * Download database as JSON file
     */
    async downloadDB() {
        const data = await this.exportDB();
        const blob = new Blob([JSON.stringify(data, null, 2)],
            { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `pos_backup_${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }

    /**
     * Import database from JSON
     */
    async importDB(data, clearFirst = true) {
        if (clearFirst) {
            await this.clearDB();
        }

        // Updated table list to match version 6 schema
        const tables = ['products', 'categories', 'pricelists', 'pricelist_items', 
            'payment_methods', 'customers', 'pos_orders', 'payments', 'config', 'sync_queue'];

        for (const [tableName, records] of Object.entries(data.tables)) {
            if (records && records.length > 0 && tables.includes(tableName)) {
                // Migrate old data to new format during import
                let migratedRecords = records;
                if (tableName === 'products') {
                    migratedRecords = records.map(record => {
                        // Convert image_emoji to image_1920 (null for file images)
                        if (record.image_emoji) {
                            return {
                                ...record,
                                image_1920: null,  // Use file image instead of emoji
                                image_emoji: undefined  // Remove old field
                            };
                        }
                        return record;
                    });
                }
                await db[tableName].bulkPut(migratedRecords);
            }
        }

        console.log('Database imported successfully');
    }

    /**
     * Load database from file input
     */
    async loadFromFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = async (e) => {
                try {
                    const data = JSON.parse(e.target.result);
                    await this.importDB(data);
                    resolve(data);
                } catch (error) {
                    reject(error);
                }
            };
            reader.onerror = reject;
            reader.readAsText(file);
        });
    }

    /**
     * Clear all database tables
     * This will also reset the initialization flag, allowing the demo data prompt to appear again
     */
    async clearDB() {
        // Updated table list to match version 6 schema
        const tables = ['products', 'categories', 'pricelists', 'pricelist_items', 
            'payment_methods', 'customers', 'pos_orders', 'payments', 'config', 'sync_queue'];
        
        await db.transaction('rw', tables, async () => {
            for (const table of tables) {
                await db[table].clear();
            }
        });
        console.log('Database cleared - initialization flag reset');
    }

    /**
     * Get database statistics
     */
    async getStats() {
        const stats = {};
        // Updated table list to match version 6 schema
        const tables = ['products', 'categories', 'pricelists', 'pricelist_items', 
            'payment_methods', 'customers', 'pos_orders', 'payments', 'config', 'sync_queue'];
        
        for (const table of tables) {
            stats[table] = await db[table].count();
        }
        return stats;
    }
}

// Global migration instance
const migration = new DBMigration();

/**
 * Mock data structure as a single JSON variable
 */
const MOCK_DATA = {
    config: {
        pos_config: {
            name: 'POS Standalone',
            currency_id: null, // Will be set from backend
            currency_name: 'IDR',
            currency_symbol: 'Rp',
            thousand_separator: '.',
            decimal_separator: ',',
            rounding_method: 'normal',
            rounding_factor: 0.01,
            business_name: 'POS Standalone',
            business_address: '',
            business_phone: '',
            business_email: '',
            receipt_header: '=== POS RECEIPT ===',
            receipt_footer: 'Thank you for shopping!',
            security_pin: '',
            sync_interval: 300,
            server_url: '',
            database_name: ''
        }
    },
    categories: [
        { id: 1, name: 'All', parent_id: null, active: true },
        { id: 2, name: 'Food', parent_id: null, active: true },
        { id: 3, name: 'Beverages', parent_id: null, active: true },
        { id: 4, name: 'Snacks', parent_id: null, active: true },
        { id: 5, name: 'Electronics', parent_id: null, active: true },
        { id: 6, name: 'Clothing', parent_id: null, active: true },
        { id: 7, name: 'Books', parent_id: null, active: true },
        { id: 8, name: 'Sports', parent_id: null, active: true },
        { id: 9, name: 'Home & Garden', parent_id: null, active: true },
        { id: 10, name: 'Toys', parent_id: null, active: true }
    ],
    products: [
        { id: 1, display_name: 'Nasi Goreng', barcode: '001', default_code: 'NASGOR', list_price: 15000, active: true, stock_qty: 50, image_1920: null, categ_id: 2 },
        { id: 2, display_name: 'Mie Ayam', barcode: '002', default_code: 'MIEAYAM', list_price: 12000, active: true, stock_qty: 30, image_1920: null, categ_id: 2 },
        { id: 3, display_name: 'Ayam Bakar', barcode: '003', default_code: 'AYAMBAKAR', list_price: 20000, active: true, stock_qty: 25, image_1920: null, categ_id: 2 },
        { id: 4, display_name: 'Soto Ayam', barcode: '004', default_code: 'SOTO', list_price: 18000, active: true, stock_qty: 20, image_1920: null, categ_id: 2 },
        { id: 5, display_name: 'Gado-Gado', barcode: '005', default_code: 'GADO', list_price: 13000, active: true, stock_qty: 15, image_1920: null, categ_id: 2 },
        { id: 6, display_name: 'Rendang', barcode: '006', default_code: 'RENDANG', list_price: 25000, active: true, stock_qty: 10, image_1920: null, categ_id: 2 },
        { id: 7, display_name: 'Satay', barcode: '007', default_code: 'SATAY', list_price: 22000, active: true, stock_qty: 35, image_1920: null, categ_id: 2 },
        { id: 8, display_name: 'Bakso', barcode: '008', default_code: 'BAKSO', list_price: 14000, active: true, stock_qty: 40, image_1920: null, categ_id: 2 },
        { id: 9, display_name: 'Es Teh Manis', barcode: '009', default_code: 'ESTEH', list_price: 5000, active: true, stock_qty: 100, image_1920: null, categ_id: 3 },
        { id: 10, display_name: 'Es Jeruk', barcode: '010', default_code: 'ESJERUK', list_price: 6000, active: true, stock_qty: 80, image_1920: null, categ_id: 3 },
        { id: 11, display_name: 'Kopi', barcode: '011', default_code: 'KOPI', list_price: 8000, active: true, stock_qty: 60, image_1920: null, categ_id: 3 },
        { id: 12, display_name: 'Teh Botol', barcode: '012', default_code: 'TEHBOTOL', list_price: 7000, active: true, stock_qty: 70, image_1920: null, categ_id: 3 },
        { id: 13, display_name: 'Air Mineral', barcode: '013', default_code: 'AIRMINERAL', list_price: 3000, active: true, stock_qty: 120, image_1920: null, categ_id: 3 },
        { id: 14, display_name: 'Jus Alpukat', barcode: '014', default_code: 'JUSALPUKAT', list_price: 12000, active: true, stock_qty: 25, image_1920: null, categ_id: 3 },
        { id: 15, display_name: 'Jus Mangga', barcode: '015', default_code: 'JUSMANGGA', list_price: 10000, active: true, stock_qty: 30, image_1920: null, categ_id: 3 }
    ],
    pricelists: [
        { id: 1, name: 'Standard', active: true },
        { id: 2, name: 'VIP', active: true },
        { id: 3, name: 'Member', active: true }
    ],
    pricelist_items: [
        { id: 1, pricelist_id: 2, product_id: 1, applied_on: '1_product', compute_price: 'percentage', percent_price: 10, min_quantity: 1 },
        { id: 2, pricelist_id: 2, product_id: 2, applied_on: '1_product', compute_price: 'percentage', percent_price: 10, min_quantity: 1 },
        { id: 3, pricelist_id: 3, product_id: 1, applied_on: '1_product', compute_price: 'percentage', percent_price: 5, min_quantity: 1 },
        { id: 4, pricelist_id: 3, product_id: 2, applied_on: '1_product', compute_price: 'percentage', percent_price: 5, min_quantity: 1 }
    ],
    payment_methods: [
        { id: 1, name: 'Cash', type: 'cash', active: true },
        { id: 2, name: 'Bank Transfer', type: 'bank', active: true },
        { id: 3, name: 'E-Wallet', type: 'ewallet', active: true },
        { id: 4, name: 'Credit Card', type: 'card', active: true }
    ],
    customers: [
        { id: 1, name: 'John Doe', email: 'john@example.com', phone: '081234567890', pricelist_id: 2 },
        { id: 2, name: 'Jane Smith', email: 'jane@example.com', phone: '081234567891', pricelist_id: 2 },
        { id: 3, name: 'Bob Wilson', email: '', phone: '081234567892', pricelist_id: null }
    ]
};

/**
 * Seed initial data for testing
 */
async function seedMockData() {
    // Check if database has been initialized (even if empty)
    const dbInitialized = await db.config.get('db_initialized');
    if (dbInitialized) {
        console.log('Database already initialized, skipping seed prompt');
        // Still load settings even if database is initialized
        await loadSettings();
        return;
    }

    // Ask user if they want to load demo data
    const loadDemo = confirm(
        '🎯 Load Demo Data?\n\n' +
        'Would you like to load sample products, categories, and pricelists?\n\n' +
        '✅ YES - Load demo data (recommended for testing)\n' +
        '❌ NO - Start with empty database'
    );

    // Mark database as initialized regardless of user choice
    await db.config.put({ key: 'db_initialized', value: true });

    if (!loadDemo) {
        console.log('User skipped demo data loading - starting with empty database');
        // Load settings even without demo data
        await loadSettings();
        return;
    }

    console.log('Seeding mock data...');

    // Categories - use existing IDs
    const catIds = {};
    for (const category of MOCK_DATA.categories) {
        const id = await db.categories.add(category);
        catIds[category.id] = id; // Map by original ID
    }

    // Products - use existing category IDs
    for (const product of MOCK_DATA.products) {
        await db.products.add({
            ...product,
            categ_id: catIds[product.categ_id] || product.categ_id  // Use mapped category ID
        });
    }

    // Pricelists - use existing IDs
    const pricelistIds = {};
    for (const pricelist of MOCK_DATA.pricelists) {
        const id = await db.pricelists.add(pricelist);
        pricelistIds[pricelist.id] = id; // Map by original ID
    }

    // Pricelist Items - use actual pricelist IDs
    for (const item of MOCK_DATA.pricelist_items) {
        await db.pricelist_items.add({
            ...item,
            pricelist_id: pricelistIds[item.pricelist_id] || item.pricelist_id,
            product_id: item.product_id  // Use original product ID
        });
    }

    // Payment Methods
    for (const method of MOCK_DATA.payment_methods) {
        await db.payment_methods.add(method);
    }

    // Customers
    for (const customer of MOCK_DATA.customers) {
        let pricelistId = null;
        if (customer.pricelist_id) {
            pricelistId = pricelistIds[customer.pricelist_id] || customer.pricelist_id;
        }
        
        await db.customers.add({
            ...customer,
            pricelist_id: pricelistId
        });
    }

    // Load settings
    await loadSettings();

    console.log('✅ Mock data seeded successfully');
    console.log('🔄 Refreshing page to load data...');

    // Reload page to ensure all data is properly loaded
    setTimeout(() => {
        window.location.reload();
    }, 1000); // Increased delay to ensure all data is saved
}

/**
 * Load settings from MOCK_DATA config or export data
 */
async function loadSettings() {
    console.log('🔧 Loading POS settings...');
    
    let settingsData = null;
    
    // Try to get from MOCK_DATA first
    if (MOCK_DATA && MOCK_DATA.config && MOCK_DATA.config.pos_config) {
        settingsData = MOCK_DATA.config.pos_config;
        console.log('📋 Using MOCK_DATA config');
    } else {
        // Fallback: try to get from export data format
        console.log('📋 MOCK_DATA.config not found, trying export data format');
        console.log('📋 MOCK_DATA structure:', MOCK_DATA);
        
        // Create default settings if no config found
        settingsData = {
            name: 'POS Standalone',
            currency_id: null,
            currency_name: 'IDR',
            currency_symbol: 'Rp',
            thousand_separator: '.',
            decimal_separator: ',',
            rounding_method: 'normal',
            rounding_factor: 0.01,
            business_name: 'POS Standalone',
            business_address: '',
            business_phone: '',
            business_email: '',
            receipt_header: '=== POS RECEIPT ===',
            receipt_footer: 'Thank you for shopping!',
            security_pin: '',
            sync_interval: 300,
            server_url: '',
            database_name: ''
        };
        console.log('📋 Using default settings');
    }
    
    console.log('📋 Available config keys:', Object.keys(settingsData));
    
    // Store in IndexedDB
    for (const [key, value] of Object.entries(settingsData)) {
        console.log(`💾 Setting ${key}:`, value);
        await db.config.put({ key, value });
    }
    
    // Also store in localStorage for UI compatibility
    localStorage.setItem('pos_settings', JSON.stringify(settingsData));
    console.log('💾 Settings also stored in localStorage for UI');
    
    // Verify settings were loaded
    const loadedSettings = {};
    for (const key of Object.keys(settingsData)) {
        const setting = await db.config.get(key);
        loadedSettings[key] = setting;
    }
    
    console.log('✅ POS settings loaded successfully:', loadedSettings);
    console.log('🎯 Settings verification complete');
}

// Initialize database
db.open().then(() => {
    console.log('✅ Database opened successfully');
    console.log('🔍 MOCK_DATA check:', typeof MOCK_DATA, MOCK_DATA ? 'defined' : 'undefined');
    if (MOCK_DATA) {
        console.log('🔍 MOCK_DATA.config check:', typeof MOCK_DATA.config, MOCK_DATA.config ? 'defined' : 'undefined');
        if (MOCK_DATA.config) {
            console.log('🔍 MOCK_DATA.config.pos_config check:', typeof MOCK_DATA.config.pos_config, MOCK_DATA.config.pos_config ? 'defined' : 'undefined');
        }
    }
    return seedMockData();
}).then(() => {
    console.log('✅ Database seeded successfully');
}).catch(err => {
    console.error('❌ Database error:', err);
});
