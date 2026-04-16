# POS Standalone - Odoo 18 Module

## 📦 Module Structure

```
pos_standalone/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── main.py
├── models/
│   ├── __init__.py
│   └── pos_standalone.py
├── security/
│   └── ir.model.access.csv
├── views/
│   ├── pos_standalone_views.xml
│   └── pos_standalone_menus.xml
└── static/
    ├── description/
    │   └── icon.png
    ├── src/
    │   └── services/
    │       └── db_service.js
    └── index.html
```

## 🎯 Features Implemented

### Backend (Odoo)

#### Models:
1. **pos.standalone.config** - Configuration management
   - Connection settings (offline/online mode)
   - Server URL and database name
   - Security PIN
   - Sync settings
   - Display preferences (currency, rounding)
   - Business information
   - Receipt customization

2. **pos.standalone.sync.log** - Sync logging
   - Track all sync operations
   - Success/failure status
   - Records synced/failed count
   - Error messages
   - Sync data (JSON)

#### Controllers:
1. **/pos_standalone** - Main POS page
2. **/pos_standalone/download** - Download standalone HTML
3. **/pos_standalone/api/sync** - Data synchronization endpoint
4. **/pos_standalone/api/export** - Export data for offline use
5. **/pos_standalone/api/import** - Import offline data

#### Views:
- Configuration form and tree views
- Sync log views with color-coded status
- Menu structure with sub-menus

#### Security:
- Access rights for POS users and managers
- Separate permissions for config and sync logs

### Frontend (Standalone)

#### Features:
- ✅ Offline-first PWA
- ✅ IndexedDB storage via Dexie.js
- ✅ Connection Settings screen
- ✅ Database Export/Import
- ✅ PIN Security
- ✅ Multi-tab order management
- ✅ Product & category management
- ✅ Customer management
- ✅ Payment processing
- ✅ Receipt generation

## 🚀 Installation

### 1. Install Module
```bash
# Copy to addons directory
cp -r pos_standalone /path/to/odoo/addons/

# Update apps list
# Odoo > Apps > Update Apps List

# Install POS Standalone
# Odoo > Apps > Search "POS Standalone" > Install
```

### 2. Access POS
```
Menu: POS Standalone > Open POS
```

### 3. Download Standalone
```
Menu: POS Standalone > Download Standalone
# Save the HTML file for offline use
```

## 📝 Configuration

### Backend Configuration
1. Go to: **POS Standalone > Configuration > Settings**
2. Create new configuration
3. Set connection mode (Offline/Online)
4. Configure display settings
5. Set business information
6. Customize receipt

### Frontend Configuration
1. Open POS Standalone
2. Click wifi icon (top right)
3. Configure connection settings
4. Set security PIN (optional)
5. Export/Import database as needed

## 🔄 Sync Workflow

### Online Mode:
1. Configure server URL, database, username, password
2. Click "Test Connection"
3. Click "Save"
4. Data will sync automatically based on interval

### Offline Mode:
1. Export database from Odoo backend
2. Import to standalone POS
3. Work offline
4. Export from standalone
5. Import back to Odoo

## 🛠️ API Endpoints

### Sync Data
```javascript
POST /pos_standalone/api/sync
{
    "config_id": 1,
    "sync_type": "manual",
    "records": [...]
}
```

### Export Data
```javascript
POST /pos_standalone/api/export
Response: {
    "success": true,
    "data": {
        "products": [...],
        "categories": [...],
        "customers": [...],
        "payment_methods": [...]
    }
}
```

### Import Data
```javascript
POST /pos_standalone/api/import
{
    "data": {
        "orders": [...]
    }
}
```

## 📊 Database Schema

### pos_standalone_config
- name, active
- connection_mode, server_url, database_name
- security_pin
- sync_interval, last_sync_date
- currency_symbol, thousand_separator, decimal_separator
- rounding_method, rounding_factor
- business_name, business_address, business_phone, business_email
- receipt_header, receipt_footer
- notes

### pos_standalone_sync_log
- name, config_id
- sync_date, sync_type
- status (success/failed/partial)
- records_synced, records_failed
- error_message, sync_data

## 🔐 Security

- PIN-based session locking
- User access rights (POS User / POS Manager)
- Secure password storage
- Session-based authentication

## 📱 PWA Features

- Installable on any device
- Offline capability
- Background sync (when online)
- Service worker caching

## 🎨 UI/UX

- Modern, responsive design
- Touch-friendly interface
- Keyboard shortcuts support
- Real-time updates
- Loading states
- Error handling

## 🐛 Troubleshooting

### WebSocket not working on file://
- Use HTTP server: `python -m http.server 8000`
- Access via: `http://localhost:8000/index.html`

### Database not syncing
- Check connection settings
- Verify server URL
- Check sync logs for errors

### Export/Import fails
- Ensure sufficient storage
- Check file format (JSON)
- Verify data integrity

## 📄 License

LGPL-3

## 👥 Author

Your Company

## 🔗 Links

- Documentation: [Link]
- Support: [Link]
- Repository: [Link]
